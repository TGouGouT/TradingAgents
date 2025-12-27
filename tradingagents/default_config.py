import os

_LLM_PROVIDER = os.getenv("TRADINGAGENTS_LLM_PROVIDER", "openai").lower()
_DEFAULT_BACKEND_URLS = {
    "openai": "https://api.openai.com/v1",
    "anthropic": "https://api.anthropic.com/",
    "google": "https://generativelanguage.googleapis.com/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "ollama": "http://localhost:11434/v1",
}
_BACKEND_URL = os.getenv("TRADINGAGENTS_BACKEND_URL") or _DEFAULT_BACKEND_URLS.get(
    _LLM_PROVIDER, "https://api.openai.com/v1"
)
_DEFAULT_QUICK_LLM = "gpt-4o-mini"
_DEFAULT_DEEP_LLM = "o4-mini"
_DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"
_DEFAULT_EMBEDDING_MAX_CHARS = 8000
if _LLM_PROVIDER == "ollama":
    _DEFAULT_QUICK_LLM = "llama3.1"
    _DEFAULT_DEEP_LLM = "qwen3"
    _DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
_QUICK_THINK_LLM = os.getenv("TRADINGAGENTS_QUICK_THINK_LLM", _DEFAULT_QUICK_LLM)
_DEEP_THINK_LLM = os.getenv("TRADINGAGENTS_DEEP_THINK_LLM", _DEFAULT_DEEP_LLM)
_EMBEDDING_MODEL = os.getenv("TRADINGAGENTS_EMBEDDING_MODEL", _DEFAULT_EMBEDDING_MODEL)
_EMBEDDING_MAX_CHARS = int(
    os.getenv("TRADINGAGENTS_EMBEDDING_MAX_CHARS", _DEFAULT_EMBEDDING_MAX_CHARS)
)

DEFAULT_CONFIG = {
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": "/Users/yluo/Documents/Code/ScAI/FR1-data",
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),
    # LLM settings
    "llm_provider": _LLM_PROVIDER,
    "deep_think_llm": _DEEP_THINK_LLM,
    "quick_think_llm": _QUICK_THINK_LLM,
    "backend_url": _BACKEND_URL,
    "embedding_model": _EMBEDDING_MODEL,
    "embedding_max_chars": _EMBEDDING_MAX_CHARS,
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Data vendor configuration
    # Category-level configuration (default for all tools in category)
    "data_vendors": {
        "core_stock_apis": "yfinance",       # Options: yfinance, alpha_vantage, local
        "technical_indicators": "yfinance",  # Options: yfinance, alpha_vantage, local
        "fundamental_data": "alpha_vantage", # Options: openai, alpha_vantage, local
        "news_data": "alpha_vantage",        # Options: openai, alpha_vantage, google, local
    },
    # Tool-level configuration (takes precedence over category-level)
    "tool_vendors": {
        # Example: "get_stock_data": "alpha_vantage",  # Override category default
        # Example: "get_news": "openai",               # Override category default
    },
}
