# clerk

Transcribe and summarize audio files automatically with AI.

## Dependencies

- Python
    - openai
    - pydub
- ffmpeg

## Environment

| key | description |
| -- | -- |
| OPENAI_API_KEY | API KEY |

## Usage

| option | description | required |
| -- | -- | :--: |
| --input | path to input sound file | ✔ |
| --transcript-output | path to output transcript file | |
| --summary-output | path to output summary file | |

```sh
python clerk.py \
  --input meeting.m4a \
  --transcript-output /path/to/output/transcript.txt \
  --summary-output /path/to/output/summary.txt
```
