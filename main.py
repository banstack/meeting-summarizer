import typer
from dotenv import load_dotenv

from audio import preprocess

# Custom hooks
from recorder import record

load_dotenv()
app = typer.Typer()


@app.command()
def run(
    do_record: bool = typer.Option(False, "--record", help="Record audio from mic"),
    file: str = typer.Option(None, "--file", help="Path to existing audio file"),
    output: str = typer.Option("summary.md", "--output", help="Output file path"),
):
    # Record nor file exists then
    if not do_record and not file:
        typer.echo("Provide --record or --file <path>")
        raise typer.Exit(1)

    # Stage 2: Record or load
    audio_path = record() if do_record else file

    # Stage 3: Pre-process
    clean_path = preprocess(file)

    # Stage 4: transcribe

    # Stage 5: summarize + export
    typer.echo(f"Audio ready at : {audio_path}")
    typer.echo(f"Clean audio ready at : {clean_path}")


if __name__ == "__main__":
    app()
