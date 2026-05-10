import json
import os
from pathlib import Path

import anthropic
import typer

MODEL = "claude-haiku-4-5-20251001"

CHUNK_SYSTEM_PROMPT = """You are an expert meeting summarizer.
Analyze the transcript excerpt and extract key information.
Respond ONLY with valid JSON — no preamble, no markdown fences.
Use this exact structure:
{
  "summary": "2-3 sentence summary of what was discussed",
  "action_items": [
    {"owner": "person name or 'unassigned'", "task": "what needs to be done"}
  ],
  "decisions": ["decision made"],
  "key_topics": ["topic 1", "topic 2"]
}
"""

COMBINE_SYSTEM_PROMPT = """You are an expert meeting summarizer.
You will receive several partial summaries of a long meeting transcript.
Combine them into one cohesive final summary.
Respond ONLY with valid JSON — no preamble, no markdown fences.
Use this exact structure:
{
  "summary": "3-5 sentence summary of the entire meeting",
  "action_items": [
    {"owner": "person name or 'unassigned'", "task": "what needs to be done"}
  ],
  "decisions": ["decision made"],
  "key_topics": ["topic 1", "topic 2"]
}"""


def summarize_and_export(chunks: list[str], output_path: str) -> str:
    """
    Summarize transcript chunks and export to markdown
    Returns the path to the output file.
    """

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    typer.echo(f"Summarizing {len(chunks)} chunk(s) with Claude...")

    if len(chunks) == 1:
        result = _summarize_chunk(client, chunks[0])
    else:
        result = _summarize_multi(client, chunks)

    output_path = _export_markdown(result, output_path)
    typer.echo(f"Summary exported -> {output_path}")

    return output_path


def _summarize_chunk(client: anthropic.Anthropic, chunk: str) -> dict:
    """
    Summarize a single chunk of transcript
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=CHUNK_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Transcript:\n\n{chunk}"}],
    )

    return _parse_response(response.content[0].text)


def _summarize_multi(client: anthropic.Anthropic, chunks: list[str]) -> dict:
    """
    Map-reduce: summarize each chunk, then combine.
    """
    partials = []

    for i, chunk in enumerate(chunks, 1):
        typer.echo(f"   Summarizing chunk {i}/{len(chunks)}...")
        partial = _summarize_chunk(client, chunk)
        partials.append(partial)

    typer.echo("    Combining partial summaries...")
    combined_text = json.dumps(partials, indent=2)

    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        system=COMBINE_SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"Partial summaires:\n\n{combined_text}"}
        ],
    )

    return _parse_response(response.content[0].text)


def _parse_response(text: str) -> str:
    """Parse JSON from Claude's response, stripping fences if present!"""
    clean = text.strip()

    if clean.startswith("```"):
        clean = clean.split("\n", 1)[1]  # strip opening fence
        clean = clean.rsplit("```", 1)[0]  # strip closing fence
    try:
        return json.loads(clean)
    except json.JSONDecodeError as e:
        typer.echo(f"Failed to parse response as JSON: {e}")
        typer.echo(f"Raw response: {text}")
        raise typer.Exit(1)


def _export_markdown(result: dict, output_path: str) -> str:
    """Write the structured summary to a markdown file"""
    lines = []

    lines.append("# Meeting Summary\n")
    lines.append(f"## TL;DR\n\n{result.get('summary', 'N/A')}\n")

    # Extract key_topics
    topics = result.get("key_topics", [])
    if topics:
        lines.append("## Key topics\n")
        for t in topics:
            lines.append(f"- {t}")
        lines.append("")

    # Extract decisions
    decisions = result.get("decisions", [])
    if decisions:
        lines.append("## Decisions\n")
        for d in decisions:
            lines.append("## Decisions\n")
        lines.append("")

    # Extract actions_items
    action_items = result.get("action_items", [])
    if action_items:
        lines.append("## Action Items\n")
        for item in action_items:
            owner = item.get("owner", "unassigned")
            task = item.get("task", "")
            lines.append(f"- **{owner}**: {task}")
        lines.append("")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    return output_path
