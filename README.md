# Meeting Summarizer CLI

Transcribe and summarize meetings from audio recordings or live mic input. Built with Whisper + Claude API

### How it works:
1. Audio / Mic as input
2. Audio pre-processing
3. Transcribe (Whisper) into text
4. Summarize with Claude (text into structured 

## How it works
- Record directly from mic or pass existing audio file
- Supports `.wav`, `.mp3`, `.mp4`, `.m4a`, `.ogg`, `.flac`
- Transcribes locally using OpenAI Whisper (no audio data leaves your machine)
- Summaarize with Claude, returns a TL:DR with key topics, decisions, and action items
- Exports to markdown

## Requirements
- Python >= 3.12
- ffmpeg
- An Anthropic API Key (or another LLM provider)

## Setup (simply)
1. Clone the repo
2. Create and activate virtual environment (standard for Python Development)
3. Install dependencies
4. Install ffmpeg
5. Add your API key

## Usage (simply)
Summarize an existing audio file
`python main.py --file recording.mp3`

Record from your mic, then summarize
`python main.py --record`

Specify output path
`python main.py --file recording.mp3 --output ~/Desktop/standup.md`

Output defaults to `summary.md` in the current directory
