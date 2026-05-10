import typer
from dotenv import load_dotenv

load_dotenv()

app = typer.Typer()


@app.command()
def run(
    record: bool = typer.Option(False, "--record", help="Record audio from mic"),
    file: str = typer.Option(None, "--file", help="Path to existing audio file"),
    output: str = typer.Option("summary.md", "--output", help="Output file path"),
):
    # Record nor file exists then
    if not record and not file:
        typer.echo("Provide --record or --file <path>")
        raise typer.Exit(1)

    # Stage 2: Record or load
    # audio_path = recorder.record() if record else file

    # Stage 3: Pre-process
    # clean_path = audio.preprocess(audio_path)

    # Stage 4: transcribe

    # Stage 5: summarize + export

    typer.echo("Pipeline stubs in place, ready to build")


if __name__ == "__main__":
    app()
