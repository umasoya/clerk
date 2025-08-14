import importlib
from .errors import UnknownModel, ProviderImplementationError

def get_summarizer(model: str, **kwargs):
    """
    model: 'openai' / 'gptoss' など。
    各アダプタは summarizer/<model>.py にあり、create(**kwargs) を公開している想定。
    """
    mod_name = f"summarizer.{model.lower()}"
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
