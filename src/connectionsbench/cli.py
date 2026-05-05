"""
ConnectionsBench CLI.
Run benchmarks and view results.
"""

from datetime import date
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich import box
from rich.console import Console
from rich.table import Table

from src.connectionsbench.loader import load_text_puzzles
from src.connectionsbench.results import (
    load_results,
    save_result,
    check_duplicate_run,
    calculate_leaderboard,
    _DEFAULT_RESULTS_DIR,
)
from src.connectionsbench.runner import run_puzzle
from src.connectionsbench.scorer import score_puzzle

load_dotenv()

app = typer.Typer(help="ConnectionsBench — benchmark LLMs on NYT Connections puzzles.")
console = Console()

_COST_PER_PUZZLE = {
    "openai:gpt-4o": 0.001,
    "openai:gpt-4o-mini": 0.00006,
    "anthropic:claude-sonnet-4-6": 0.001,
    "anthropic:claude-haiku-4-5": 0.0005,
    "anthropic:claude-opus-4-7": 0.002,
    "google-gla:gemini-1.5-flash": 0.0,
    "google-gla:gemini-1.5-pro": 0.0005,
}


@app.command()
def run(
        model: str = typer.Option(..., help="PydanticAI model string e.g. openai:gpt-4o"),
        limit: int = typer.Option(None, help="Max number of puzzles to run"),
        from_date: str = typer.Option(None, "--from", help="Start date YYYY-MM-DD"),
        to_date: str = typer.Option(None, "--to", help="End date YYYY-MM-DD"),
        dry_run: bool = typer.Option(False, "--dry-run", help="Validate without calling the API"),
        force: bool = typer.Option(False, "--force", help="Overwrite existing results"),
        data_file: Path = typer.Option(None, help="Path to connections.json dataset"),
        results_dir: Path = typer.Option(None, help="Path to results directory"),
):
    """Run a benchmark against a model."""
    rdir = results_dir or _DEFAULT_RESULTS_DIR

    kwargs = {}
    if data_file:
        kwargs["data_file"] = data_file

    puzzles = load_text_puzzles(**kwargs)

    if from_date:
        from_dt = date.fromisoformat(from_date)
        puzzles = [p for p in puzzles if p.date >= from_dt]
    if to_date:
        to_dt = date.fromisoformat(to_date)
        puzzles = [p for p in puzzles if p.date <= to_dt]
    if limit:
        puzzles = puzzles[:limit]

    if not puzzles:
        console.print("[red]No puzzles found for the given filters.[/red]")
        raise typer.Exit(1)

    puzzle_ids = [p.id for p in puzzles]
    all_duplicate, already_run = check_duplicate_run(model, puzzle_ids, rdir)

    if all_duplicate and not force:
        console.print(
            f"[yellow]Results for {model} already cover all {len(puzzle_ids)} selected puzzles. "
            f"Use --force to overwrite.[/yellow]"
        )
        raise typer.Exit(0)

    if already_run and not force:
        skipping = len(already_run)
        puzzles = [p for p in puzzles if p.id not in already_run]
        console.print(f"[dim]Skipping {skipping} already-run puzzles. {len(puzzles)} remaining.[/dim]")

    date_range = f"{puzzles[0].date} → {puzzles[-1].date}"
    cost = _COST_PER_PUZZLE.get(model)
    cost_str = f"~${cost * len(puzzles):.2f}" if cost is not None else "unknown"

    console.print(f"\n[bold]ConnectionsBench Run[/bold]")
    console.print(f"  Model:    {model}")
    console.print(f"  Puzzles:  {len(puzzles)} ({date_range})")
    console.print(f"  Est cost: {cost_str}")

    if dry_run:
        console.print("\n[green]Dry run complete — no API calls made.[/green]")
        raise typer.Exit(0)

    typer.confirm(f"\nRun {len(puzzles)} puzzles against {model}?", abort=True)

    solved = 0
    for i, puzzle in enumerate(puzzles, 1):
        try:
            answer = run_puzzle(puzzle, model)
            result = score_puzzle(puzzle, answer, model)
            save_result(result, model, rdir)
            status = "✓" if result.solved else "✗"
            console.print(f"  [{i}/{len(puzzles)}] #{puzzle.id} {puzzle.date} {status} ({result.groups_correct}/4)")
            if result.solved:
                solved += 1
        except Exception as e:
            console.print(f"  [{i}/{len(puzzles)}] #{puzzle.id} {puzzle.date} [red]ERROR: {e}[/red]")

    console.print(f"\n[bold]Done.[/bold] Solved {solved}/{len(puzzles)} ({solved / len(puzzles) * 100:.1f}%)")


@app.command()
def results(
        model: str = typer.Option(None, help="Filter by model name"),
        provider: str = typer.Option(None, help="Filter by provider e.g. openai"),
        results_dir: Path = typer.Option(None, help="Path to results directory"),
):
    """View benchmark leaderboard."""
    rdir = results_dir or _DEFAULT_RESULTS_DIR

    if not rdir.exists() or not list(rdir.glob("*.jsonl")):
        console.print("[yellow]No results found. Run a benchmark first.[/yellow]")
        raise typer.Exit(0)

    results_by_model = {}
    for path in rdir.glob("*.jsonl"):
        m = path.stem.replace("_", ":", 1)
        results_by_model[m] = load_results(m, rdir)

    if model:
        results_by_model = {k: v for k, v in results_by_model.items() if model in k}
    if provider:
        results_by_model = {k: v for k, v in results_by_model.items() if k.startswith(provider)}

    if not results_by_model:
        console.print("[yellow]No results found for the given filters.[/yellow]")
        raise typer.Exit(0)

    leaderboard = calculate_leaderboard(results_by_model)
    _print_leaderboard(leaderboard)


def _print_leaderboard(rows: list[dict]) -> None:
    table = Table(box=box.SIMPLE_HEAVY, show_header=True, header_style="bold")
    table.add_column("Model", style="cyan")
    table.add_column("Puzzles", justify="right")
    table.add_column("Solve%", justify="right")
    table.add_column("Avg Groups", justify="right")
    table.add_column("Yellow%", justify="right")
    table.add_column("Green%", justify="right")
    table.add_column("Blue%", justify="right")
    table.add_column("Purple%", justify="right")
    table.add_column("Gap", justify="right")

    for row in rows:
        table.add_row(
            row["model"],
            str(row["puzzle_count"]),
            f"{row['solve_pct']:.1f}%",
            f"{row['avg_groups']:.2f}",
            f"{row['yellow_pct']:.1f}%",
            f"{row['green_pct']:.1f}%",
            f"{row['blue_pct']:.1f}%",
            f"{row['purple_pct']:.1f}%",
            f"{row['purple_gap']:.1f}pp",
        )

    console.print(table)


if __name__ == "__main__":
    app()
