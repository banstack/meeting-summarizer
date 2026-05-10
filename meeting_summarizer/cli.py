import typer
from dotenv import load_dotenv

from meeting_summarizer.audio import preprocess
from meeting_summarizer.recorder import record
from meeting_summarizer.summarizer import summarize_and_export
from meeting_summarizer.transcriber import chunk_transcript, save_transcript, transcribe

load_dotenv()
app = typer.Typer()


@app.command()
def run(
    do_record: bool = typer.Option(False, "--record", help="Record audio from mic"),
    file: str = typer.Option(None, "--file", help="Path to existing audio file"),
    output: str = typer.Option("summary.md", "--output", help="Output file path"),
):
    if not do_record and not file:
        typer.echo("Provide --record or --file <path>")
        raise typer.Exit(1)

    audio_path = record() if do_record else file

    typer.echo("=== Pre-processing Stage ===\n")
    clean_path = preprocess(audio_path)

    typer.echo("\n=== Transcribing Phase ===\n")
    transcript = transcribe(clean_path)
    save_transcript(transcript, clean_path)
    chunks = chunk_transcript(transcript)

    typer.echo("\n=== Summarizing ===\n")
    summarize_and_export(chunks, output)


def main():
    app()
