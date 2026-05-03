"""
Results loading and leaderboard calculation for ConnectionsBench.
"""

from pathlib import Path

from src.connectionsbench.models import PuzzleResult

_DEFAULT_RESULTS_DIR = Path(__file__).parent.parent.parent / "results"


def load_results(model: str, results_dir: Path = _DEFAULT_RESULTS_DIR) -> list[PuzzleResult]:
    path = results_dir / f"{model.replace(':', '_')}.jsonl"
    if not path.exists():
        return []
    with open(path) as f:
        return [PuzzleResult.model_validate_json(line) for line in f if line.strip()]


def save_result(result: PuzzleResult, model: str, results_dir: Path = _DEFAULT_RESULTS_DIR) -> None:
    """Append a single PuzzleResult to the model's JSONL file."""
    results_dir.mkdir(parents=True, exist_ok=True)
    path = results_dir / f"{model.replace(':', '_')}.jsonl"
    with open(path, "a") as f:
        f.write(result.model_dump_json() + "\n")


def get_run_puzzle_ids(model: str, results_dir: Path = _DEFAULT_RESULTS_DIR) -> set[int]:
    """Return set of puzzle IDs already run for a given model."""
    return {r.puzzle_id for r in load_results(model, results_dir)}


def check_duplicate_run(model: str, puzzle_ids: list[int], results_dir: Path = _DEFAULT_RESULTS_DIR) -> tuple[
    bool, set[int]]:
    """
    Check if all puzzles in puzzle_ids have already been run for this model.
    """
    already_run = get_run_puzzle_ids(model, results_dir)
    overlap = already_run & set(puzzle_ids)
    all_duplicate = overlap == set(puzzle_ids)
    return all_duplicate, overlap


def calculate_leaderboard():
    pass


def calculate_model_metrics(model: str, results: list[PuzzleResult]) -> dict:
    """Calculate metrics for a single model."""
    total = len(results)

    return {
        "puzzle_count": total,
    }
