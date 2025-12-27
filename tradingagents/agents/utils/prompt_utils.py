def _truncate_text(text, max_chars):
    if len(text) <= max_chars:
        return text
    separator = "\n...\n"
    half = max((max_chars - len(separator)) // 2, 0)
    return f"{text[:half]}{separator}{text[-half:]}"


def _chunk_text(text, max_chars):
    if len(text) <= max_chars:
        return [text]
    parts = text.split("\n\n")
    chunks = []
    current = []
    current_len = 0
    for part in parts:
        part_len = len(part)
        if part_len > max_chars:
            if current:
                chunks.append("\n\n".join(current))
                current = []
                current_len = 0
            for i in range(0, part_len, max_chars):
                chunks.append(part[i:i + max_chars])
            continue
        extra_len = part_len + (2 if current else 0)
        if current_len + extra_len <= max_chars:
            current.append(part)
            current_len += extra_len
        else:
            chunks.append("\n\n".join(current))
            current = [part]
            current_len = part_len
    if current:
        chunks.append("\n\n".join(current))
    return chunks


def _summarize_chunk(llm, text, target_chars):
    prompt = (
        "Summarize the text for a trading debate. "
        "Preserve tickers, dates, prices, indicators, and specific claims. "
        f"Limit to {target_chars} characters.\n\n"
        f"{text}"
    )
    try:
        response = llm.invoke(prompt)
        summary = getattr(response, "content", "") or ""
        summary = summary.strip()
    except Exception:
        summary = ""
    if not summary:
        return _truncate_text(text, target_chars)
    return _truncate_text(summary, target_chars)


def _summarize_text(llm, text, target_chars, chunk_chars, max_passes):
    if len(text) <= target_chars:
        return text
    working = text
    passes = max(max_passes, 1)
    for _ in range(passes):
        if len(working) <= target_chars:
            return working
        chunks = _chunk_text(working, chunk_chars)
        if len(chunks) == 1:
            working = _summarize_chunk(llm, working, target_chars)
            continue
        per_chunk_target = max(target_chars // len(chunks), 200)
        summaries = []
        for chunk in chunks:
            summaries.append(_summarize_chunk(llm, chunk, per_chunk_target))
        working = "\n".join(summaries).strip()
    return _truncate_text(working, target_chars)


def _truncate_sections(sections, max_chars, min_chars):
    total_len = sum(len(value) for value in sections.values())
    if total_len <= max_chars:
        return sections
    keys = list(sections)
    if not keys:
        return sections
    min_total = min_chars * len(keys)
    if min_total > max_chars:
        min_chars = max(0, max_chars // len(keys))
        min_total = min_chars * len(keys)
    remaining = max_chars - min_total
    total_len = total_len or 1
    caps = {}
    allocated = 0
    for key in keys:
        share = int(len(sections[key]) / total_len * remaining)
        caps[key] = min_chars + share
        allocated += caps[key]
    leftover = max_chars - allocated
    if leftover > 0:
        caps[keys[0]] += leftover
    return {key: _truncate_text(value, caps[key]) for key, value in sections.items()}


def limit_prompt_sections(config, llm, sections):
    if config.get("llm_provider", "").lower() != "ollama":
        return sections
    max_chars = int(config.get("ollama_prompt_max_chars", 8000))
    if max_chars <= 0:
        return {key: "" for key in sections}
    min_chars = int(config.get("ollama_prompt_min_section_chars", 200))
    chunk_chars = int(config.get("ollama_prompt_chunk_chars", 2000))
    summarize_passes = int(config.get("ollama_prompt_summarize_passes", 3))
    if not llm or summarize_passes <= 0:
        return _truncate_sections(sections, max_chars, min_chars)
    working = dict(sections)
    for _ in range(summarize_passes):
        total_len = sum(len(value) for value in working.values())
        if total_len <= max_chars:
            return working
        ratio = max_chars / max(total_len, 1)
        for key, value in working.items():
            target = max(min_chars, int(len(value) * ratio))
            if len(value) > target:
                working[key] = _summarize_text(llm, value, target, chunk_chars, summarize_passes)
    return _truncate_sections(working, max_chars, min_chars)
