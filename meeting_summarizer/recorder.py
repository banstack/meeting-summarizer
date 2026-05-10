from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf
import typer

SAMPLE_RATE = 16_000  # Hz which is enough for speech, Whisper expects
CHANNELS = 1


def record(output_dir: str = ".") -> str:
    """
    Record audio from the default mic until the user presses Enter.
    Returns the path to the saved .wav file.
    """
    chunks = []

    def callback(indata, frames, time, status):
        if status:
            typer.echo(f"[Warning] {status}")
        # Receive view into buffer that gets overwritten
        # Prevent list of references pointing to old chunk
        chunks.append(indata.copy())

    filename = _build_filename(output_dir)

    typer.echo("Recording... press Enter to stop.")
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, callback=callback):
        # Block main thread while InputStream runs in background thread
        input()

    if not chunks:
        typer.echo("No audio caputured.")
        raise typer.Exit(1)

    # Numpy to concate chunks into wav file
    audio = np.concatenate(chunks, axis=0)
    sf.write(filename, audio, SAMPLE_RATE)

    duration = len(audio) / SAMPLE_RATE
    typer.echo(f"Saved {duration:.1f}s of audio for {filename}")

    return filename


def _build_filename(output_dir: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = Path(output_dir) / f"recording_{timestamp}.wav"
    path.parent.mkdir(parents=True, exist_ok=True)
    return str(path)
