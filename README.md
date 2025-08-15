<p align="center">
  <img src="img/clerk_1024x1024.png" alt="clerk_logo" width="300">
</p>

# clerk

Transcribe and summarize audio files automatically with AI.

## Dependencies

- Python
    - openai
    - pydub
    - httpx
- ffmpeg

## Environment

| key | description |
| -- | -- |
| OPENAI_API_KEY | API KEY |
| LLM_MODEL | llm model |
| GPT_OSS_BASE_URL | gpt-oss server url |

## Usage

| option | description | required |
| -- | -- | :--: |
| --input | path to input sound file | ✔ |
| --transcript-output | path to output transcript file | |
| --summary-output | path to output summary file | |
| --summarize | enable or disable summarization. choice [yes(default), none] | |

```sh
python clerk.py \
  --input meeting.m4a \
  --transcript-output /path/to/output/transcript.txt \
  --summary-output /path/to/output/summary.txt
```
