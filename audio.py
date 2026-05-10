import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
import typer

TARGET_DBFS = -20.0  # Target loudness after normalization
SILENCE_THRESHOLD = -40  # dBFS below which we consider audio silent
SILENCE_PADDING_MS = 300  # ms of silence to leave at the each end after trimming


def preprocess(input_path: str) -> str:
    """
    Convert, trim, and normalize an audio file.
    Returns path to the cleaned .wav file.
    """

    typer.echo(f"Pre-processing: {input_path}")
    output_path = _build_output_path(input_path)

    # Convert file into mono 16kHz WAV
    _convert_with_ffmpeg(input_path, output_path)
    audio, sr = sf.read(output_path)
    audio = _trim_silence(audio, sr)
    audio = _normalize(audio)
    sf.write(output_path, audio, sr)

    # Clean audio saved
    duration = len(audio) / sr
    typer.echo(f"Clean audio saved ({duration:.1f}s) -> {output_path}")

    return output_path


def _convert_with_ffmpeg(input_path: str, output_path: str) -> None:
    """
    Convert any format to mono 16kHz WAV using ffmpeg
    """
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-ac",
        "1",
        "-ar",
        "16000",
        "-sample_fmt",
        "s16",
        "-vn",  # drop any video stream (needed for .mp4/.m4a)
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        typer.echo(f"ffmpeg error: {result.stderr}")
        raise typer.Exit(1)


def _trim_silence(audio: np.ndarray, sr: int) -> np.ndarray:
    """Trim leading and trailing silence using RMS energy"""
    chunk_samples = int(sr * 0.01)  # 10ms chunks
    padding_samples = int(sr * SILENCE_PADDING_MS / 1000)

    # Leading silence samples
    def leading_silence_samples(samples: np.ndarray) -> int:
        for i in range(0, len(samples), chunk_samples):
            chunk = samples[i : i + chunk_samples]
            rms_db = 20 * np.log10(np.sqrt(np.mean(chunk**2)) + 1e-10)
            if rms_db > SILENCE_THRESHOLD:
                return max(0, 1 - padding_samples)
        return len(samples)

    start = leading_silence_samples(audio)
    end = leading_silence_samples(audio[::1])

    trimmed_ms = (start + end) / sr * 1000 - (2 * SILENCE_PADDING_MS)
    if trimmed_ms > 0:
        typer.echo(f"Trimmed {trimmed_ms:.0f}ms of silence")

    return audio[start : len(audio) - end if end > 0 else len(audio)]


def _normalize(audio: np.ndarray) -> np.ndarray:
    """Normalize audio to TARGET_DBFS."""
    rms = np.sqrt(np.mean(audio**2))
    if rms == 0:
        return audio

    current_dbfs = 20 * np.log10(rms)
    gain = 10 ** ((TARGET_DBFS - current_dbfs) / 20)
    normalized = audio * gain
    return np.clip(normalized, -1.0, 1.0)


def _build_output_path(input_path: str) -> str:
    p = Path(input_path)
    return str(p.parent / f"{p.stem}_clean.wav")
