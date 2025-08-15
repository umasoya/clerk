# clerk.py
import os
import argparse
from pathlib import Path
from math import ceil

from pydub import AudioSegment
import whisper

from summarizer import get_summarizer
from core.factory import get_provider_for_model  # ← MODELからPROVIDERを取得


# ---- Transcribe (Whisper local) ----
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL", "base")
whisper_model = whisper.load_model(WHISPER_MODEL_NAME)


def split_audio(file_path: str, chunk_length_minutes: int) -> list[str]:
    """
    入力ファイルを chunk/ 以下に mp3 で分割して保存し、パスの配列を返す。
    """
    src = Path(file_path)
    if not src.exists():
        raise FileNotFoundError(f"input not found: {file_path}")

    out_dir = Path("chunk")
    out_dir.mkdir(parents=True, exist_ok=True)

    input_format = src.suffix.lstrip(".")  # 例: "m4a"
    output_format = "mp3"                  # m4a は書けない環境が多いので mp3 に固定

    audio = AudioSegment.from_file(src, format=input_format)
    chunk_ms = chunk_length_minutes * 60 * 1000
    total_chunks = max(1, ceil(len(audio) / chunk_ms))
    paths: list[str] = []

    for i in range(total_chunks):
        start = i * chunk_ms
        end = min(start + chunk_ms, len(audio))
        chunk = audio[start:end]
        out = out_dir / f"chunk_{i + 1}.{output_format}"
        chunk.export(out, format=output_format)
        paths.append(str(out))

    return paths


def transcribe_audio(file_path: str) -> str:
    """
    Whisper で単一オーディオを文字起こし。
    """
    result = whisper_model.transcribe(file_path)
    return result["text"]


def summarize_text(
    text: str,
    *,
    model: str,
    temperature: float | None = None,
    style: str | None = None,
    language: str | None = None,
) -> str:
    """
    MODEL だけ受け取り、factory側のテーブルで PROVIDER を決定して要約する。
    プロンプトは core/prompt.py の日本語デフォルト（議事録向け）を使用。
    """
    provider = get_provider_for_model(model)

    summarizer = get_summarizer(
        provider,
        model=model,
        # 代表的な引数（必要なら環境変数から渡す）
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("GPT_OSS_BASE_URL"),
    )

    options = {}
    if temperature is not None:
        options["temperature"] = temperature

    return summarizer.summarize(
        text,
        style=style,
        language=language,
        options=(options or None),
    )


def main():
    parser = argparse.ArgumentParser(
        description="音声ファイルを文字起こしし、要約を作成します。"
    )
    parser.add_argument("--input", required=True, help="入力音声ファイルのパス（例: meeting.m4a）")
    parser.add_argument("--transcript-output", default="transcript.txt", help="文字起こしの出力パス")
    parser.add_argument("--summary-output", default="summary.txt", help="要約の出力パス")
    parser.add_argument("--summarize", choices=["yes", "none"], default="yes", help="yes: 要約する / none: しない")
    parser.add_argument("--chunk-minutes", type=int, default=5, help="音声分割単位（分）")

    # モデルは必須 or 環境変数 LLM_MODEL から
    parser.add_argument(
        "--model",
        default=os.getenv("LLM_MODEL", None),
        required=True
        help="使用モデル（例: gpt-4o-mini, gpt-oss-20b）",
    )

    # 追加パラメータ（任意）
    parser.add_argument("--temperature", type=float, default=0.2, help="生成温度（例: 0.5）")
    parser.add_argument("--style", default=None, help="スタイル指示（例: 箇条書きで簡潔に）")
    parser.add_argument("--language", default="日本語", help="出力言語（例: 日本語, 英語）")

    args = parser.parse_args()

    # --- Split & Transcribe ---
    chunk_files = split_audio(args.input, args.chunk_minutes)

    all_transcripts: list[str] = []
    for path in chunk_files:
        print(f"[INFO] Transcribing {path} ...")
        text = transcribe_audio(path)
        all_transcripts.append(text)

    full_text = "\n".join(all_transcripts)
    print("[INFO] Transcription complete.")

    with open(args.transcript_output, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"[DONE] 文字起こしを {args.transcript_output} に出力しました。")

    # --- Summarize ---
    if args.summarize == "yes":
        print("[INFO] Generating summary ...")
        summary = summarize_text(
            full_text,
            model=args.model,
            temperature=args.temperature,
            style=args.style,
            language=args.language,
        )
        with open(args.summary_output, "w", encoding="utf-8") as f:
            f.write(summary)
        print(f"[DONE] 要約を {args.summary_output} に出力しました。")
    else:
        print("[INFO] 要約はスキップしました。")


if __name__ == "__main__":
    main()
