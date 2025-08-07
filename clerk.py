import os
import openai
import argparse
from pydub import AudioSegment
from math import ceil

# ✅ Whisper API
openai.api_key = os.environ.get("OPENAI_API_KEY")


def split_audio(file_path, chunk_length_minutes):
    audio_format = os.path.splitext(file_path)[1][1:]  # 拡張子からフォーマット取得（例: m4a, mp3）
    audio = AudioSegment.from_file(file_path, format=audio_format)
    chunk_length_ms = chunk_length_minutes * 60 * 1000
    total_chunks = ceil(len(audio) / chunk_length_ms)
    chunk_paths = []

    for i in range(total_chunks):
        start = i * chunk_length_ms
        end = min(start + chunk_length_ms, len(audio))
        chunk = audio[start:end]
        chunk_path = f"chunk_{i+1}.{audio_format}"
        chunk.export(chunk_path, format=audio_format)
        chunk_paths.append(chunk_path)

    return chunk_paths


def transcribe_audio(file_path):
    with open(file_path, "rb") as f:
        transcript = openai.Audio.transcribe("whisper-1", f)
        return transcript["text"]


def summarize_text(text):
    messages = [
        {"role": "system", "content": "あなたは優秀な議事録作成者です。"},
        {"role": "user", "content": f"以下の音声文字起こし結果を要約してください：\n{text}"}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        temperature=0.5,
    )

    return response["choices"][0]["message"]["content"]


def main():
    parser = argparse.ArgumentParser(description="音声ファイルを文字起こしし、要約を作成します。")
    parser.add_argument("--input", required=True, help="入力音声ファイルのパス（例: meeting.m4a）")
    parser.add_argument("--transcript-output", default="transcript.txt", help="文字起こしファイルの出力パス")
    parser.add_argument("--summary-output", default="summary.txt", help="要約ファイルの出力パス")
    parser.add_argument("--chunk-minutes", type=int, default=5, help="音声分割単位（分）")

    args = parser.parse_args()

    chunk_files = split_audio(args.input, args.chunk_minutes)

    all_transcripts = []
    for path in chunk_files:
        print(f"[INFO] Transcribing {path} ...")
        text = transcribe_audio(path)
        all_transcripts.append(text)

    full_text = "\n".join(all_transcripts)
    print("[INFO] Transcription complete.")

    print("[INFO] Generating summary ...")
    summary = summarize_text(full_text)

    with open(args.transcript_output, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"[DONE] 文字起こしを {args.transcript_output} に出力しました。")

    with open(args.summary_output, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"[DONE] 要約を {args.summary_output} に出力しました。")


if __name__ == "__main__":
    main()
