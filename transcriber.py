from pathlib import Path

import tiktoken  # Open AI's
import typer
import whisper

WHISPER_MODEL = "base"  # Tiny, Base, Small, Medium, Large
MAX_TOKENS = 2000  # Limit to 2k tokens per chunk
CHUNK_OVERLAP = 100  # tokens of overlap between chunks (prevent context loss)


def transcribe(audio_path: str) -> str:
    """
    Transcribe a WAV file using Whisper.
    Returns the full transcript as a string.
    """
    typer.echo(f"Loading Whisper model ({WHISPER_MODEL})...")
    model = whisper.load_model(WHISPER_MODEL)

    typer.echo("Transcribing audio...")
    # Disable fp16 as it caused issues on Apple Silicon
    result = model.transcribe(audio_path, fp16=False, language="en")
    transcript = result["text"].strip()

    typer.echo(f"Transcription complete - {len(transcript.split())} words")
    return transcript


def chunk_transcript(transcript: str) -> list[str]:
    """
    Split a transcript into overlapping chunks by token count.
    Returns a list of text chunks ready for the LLM
    """
    # Utilize tokenizer used by GPT-4 and Claude's API pricing (token alignment)
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(transcript)
    typer.echo(
        f"\nPre-chunk counts: {len(transcript.split())} words, {len(transcript)} chars, {len(tokens)} tokens"
    )

    if len(tokens) <= MAX_TOKENS:
        typer.echo("\nTranscript fits in one chunk : skipping split")
        return [transcript]

    chunks = []
    start = 0

    while start < len(tokens):
        end = min(start + MAX_TOKENS, len(tokens))
        chunk_tokens = tokens[start:end]
        chunks.append(enc.decode(chunk_tokens))
        if end == len(tokens):
            break
        start += MAX_TOKENS - CHUNK_OVERLAP  # Step forward with overlap

    typer.echo(f"Split into {len(chunks)} chunks ({len(tokens)} total tokens)")
    return chunks


def save_transcript(transcript: str, audio_path: str) -> str:
    """
    Save raw transcript to a .txt file alongside the audio.
    Useful for debugging without re-running Whisper.
    """
    p = Path(audio_path)
    out_path = str(p.parent / f"{p.stem}_transcript.txt")
    with open(out_path, "w") as f:
        f.write(transcript)
    typer.echo(f"Transcript saved: {out_path}")
    return out_path
