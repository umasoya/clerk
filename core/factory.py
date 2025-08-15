import importlib
from .errors import UnknownModel, ProviderImplementationError

MODEL_PROVIDER_MAP = {
    # OpenAI
    "gpt-4o-mini": "openai",
    "gpt-4o": "openai",

    # gpt-oss
    "gpt-oss-20b": "gptoss",
    "gpt-oss-13b": "gptoss",

    # Anthropic
    "claude-3-haiku": "anthropic",
    "claude-3-opus": "anthropic",
}

def get_provider_for_model(model: str) -> str:
    try:
        return MODEL_PROVIDER_MAP[model]
    except KeyError as e:
        raise UnknownProvider(f"Unknown model in MODEL_PROVIDER_MAP: {model}") from e

def get_summarizer(provider: str, **kwargs):
    mod_name = f"summarizer.{provider.lower()}"
    try:
        mod = importlib.import_module(mod_name)
    except ModuleNotFoundError as e:
        raise UnknownProvider(provider) from e

    if not hasattr(mod, "create"):
        raise ProviderImplementationError(f"{mod_name} must define create(**kwargs)")
    summarizer = mod.create(**kwargs)
    if not hasattr(summarizer, "summarize"):
        raise ProviderImplementationError(f"{mod_name}.create() must return an object with summarize(...)")
    return summarizer
