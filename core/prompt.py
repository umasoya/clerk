# デフォルトの system メッセージ（議事録用）
BASE_SUMMARY_SYSTEM = "あなたは優秀な議事録作成者です。"

def build_user_prompt(
    text: str,
    style: str | None = None,
    language: str | None = None,
) -> str:
    """
    style: 追加のスタイル指定（例: 簡潔に、箇条書きで）
    language: 出力言語（例: 日本語, 英語）
    text: 要約対象の文字列
    """
    lines: list[str] = []

    # 任意でスタイル指定
    if style:
        lines.append(f"スタイル: {style}")

    # 任意で出力言語指定
    if language:
        lines.append(f"言語: {language}")

    # 固定の前置き + 本文
    lines.append(f"以下の音声文字起こし結果を要約してください：\n{text}")

    return "\n".join(lines)
