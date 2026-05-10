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

## Usage
**Summarize an existing audio file**
 
```bash
python main.py --file recording.mp3
```
 
**Record from your mic, then summarize**
 
```bash
python main.py --record
# speak, then press Enter to stop recording
```
 
**Specify output path**
 
```bash
python main.py --file recording.mp3 --output ~/Desktop/standup.md
```
 
Output defaults to `summary.md` in the current directory.

## Expected Output
```markdown
# Meeting Summary
 
## TL;DR
The team aligned on Q3 priorities with the onboarding redesign as the
top deliverable. Concerns were raised about the timeline given current resourcing.
 
## Key Topics
- Q3 roadmap
- Onboarding redesign
- Resourcing
 
## Decisions
- Onboarding flow ships before end of quarter
- Design review moved to Thursdays
 
## Action Items
- **Alice**: Share revised wireframes by Friday
- **unassigned**: Schedule follow-up with the data team
```

## Configuration
Edit constants at the top of each module to tune behaviour:
 
| File | Constant | Default | Description |
|---|---|---|---|
| `transcriber.py` | `WHISPER_MODEL` | `base` | Whisper model size: `tiny` `base` `small` `medium` `large` |
| `transcriber.py` | `MAX_TOKENS` | `2000` | Max tokens per chunk sent to Claude |
| `audio.py` | `TARGET_DBFS` | `-20.0` | Target loudness after normalization |
| `audio.py` | `SILENCE_THRESHOLD` | `-40` | dBFS below which audio is treated as silence |
 
Larger Whisper models are more accurate but slower. `small` is a good middle ground for production use.
 
