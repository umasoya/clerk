import os
from typing import Optional, Dict, Any
try:
    from openai import OpenAI
except Exception as e:  # ライブラリ未導入時の分かりやすいエラー
    raise RuntimeError("openai パッケージが必要です: pip install openai") from e

from core.prompt import BASE_SUMMARY_SYSTEM, build_user_prompt

class _OpenAISummarizer:
    def __init__(self, model: str, api_key: Optional[str] = None, **_: Any):
        self.model = model
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

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

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return resp.choices[0].message.content.strip()

def create(**kwargs):
    """
    例: create(model="gpt-4o-mini", api_key="sk-...")
    """
    return _OpenAISummarizer(**kwargs)
