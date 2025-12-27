from openai import OpenAI
from .config import get_config


def _extract_response_text(response):
    output_text = getattr(response, "output_text", None)
    if output_text:
        return output_text

    texts = []
    output = getattr(response, "output", None)
    if isinstance(output, list):
        for item in output:
            item_content = item.get("content") if isinstance(item, dict) else getattr(item, "content", None)
            if item_content:
                for content_item in item_content:
                    text = content_item.get("text") if isinstance(content_item, dict) else getattr(content_item, "text", None)
                    if text:
                        texts.append(text)
                continue
            text = item.get("text") if isinstance(item, dict) else getattr(item, "text", None)
            if text:
                texts.append(text)

    if texts:
        return "\n".join(texts).strip()

    raise RuntimeError("OpenAI response did not include output text")


def _use_legacy_openai_output(config):
    return config.get("llm_provider", "").lower() == "openai"


def _select_response_text(response, config):
    if _use_legacy_openai_output(config):
        return response.output[1].content[0].text
    return _extract_response_text(response)


def get_stock_news_openai(query, start_date, end_date):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    response = client.responses.create(
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search Social Media for {query} from {start_date} to {end_date}? Make sure you only get the data posted during that period.",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    return _select_response_text(response, config)


def get_global_news_openai(curr_date, look_back_days=7, limit=5):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    response = client.responses.create(
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search global or macroeconomics news from {look_back_days} days before {curr_date} to {curr_date} that would be informative for trading purposes? Make sure you only get the data posted during that period. Limit the results to {limit} articles.",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    return _select_response_text(response, config)


def get_fundamentals_openai(ticker, curr_date):
    config = get_config()
    client = OpenAI(base_url=config["backend_url"])

    response = client.responses.create(
        model=config["quick_think_llm"],
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": f"Can you search Fundamental for discussions on {ticker} during of the month before {curr_date} to the month of {curr_date}. Make sure you only get the data posted during that period. List as a table, with PE/PS/Cash flow/ etc",
                    }
                ],
            }
        ],
        text={"format": {"type": "text"}},
        reasoning={},
        tools=[
            {
                "type": "web_search_preview",
                "user_location": {"type": "approximate"},
                "search_context_size": "low",
            }
        ],
        temperature=1,
        max_output_tokens=4096,
        top_p=1,
        store=True,
    )

    return _select_response_text(response, config)
