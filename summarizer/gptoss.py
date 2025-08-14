import os
from typing import Optional, Dict, Any

try:
    import httpx
except Exception as e:
    raise RuntimeError("httpx パッケージが必要です: pip install httpx") from e

from core.prompt import BASE_SUMMARY_SYSTEM, build_user_prompt

class _GptOssSummarizer:
    def __init__(self, model: str, base_url: Optional[str] = None, timeout: int = 120, **_: Any):
        self.model = model
        self.base_url = base_url or os.getenv("GPT_OSS_BASE_URL", "http://127.0.0.1:1234/v1")
        self.timeout = timeout

    def _chat(self, system: str, user: str, temperature: float = 0.2) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
        }
        with httpx.Client(timeout=self.timeout) as client:
            r = client.post(f"{self.base_url}/chat/completions", json=payload)
            r.raise_for_status()
            data = r.json()
        return data["choices"][0]["message"]["content"].strip()

    def summarize(
        self,
        text: str,
        *,
        style: Optional[str] = None,
        language: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        options = options or {}
        system = BASE_SUMMARY_SYSTEM
        temperature = options.get("temperature", 0.2)
        prompt = build_user_prompt(text, style, language)
        return self._chat(system, prompt, temperature=temperature)

def create(**kwargs):
    """
    例: create(model="openai/gpt-oss-20b", base_url="http://127.0.0.1:1234/v1")
    """
    return _GptOssSummarizer(**kwargs)
