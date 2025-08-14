# Public API を薄く再エクスポート（呼び出し側が覚えるのは get_summarizer だけでOK）
from core.factory import get_summarizer

__all__ = ["get_summarizer"]
