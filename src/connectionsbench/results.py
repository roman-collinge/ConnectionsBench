"""
Results loading and leaderboard calculation for ConnectionsBench.
"""

from pathlib import Path

from src.connectionsbench.models import PuzzleResult, Tier

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
    solved = sum(1 for r in results if r.solved)
    avg_groups = sum(r.groups_correct for r in results) / total

    tier_accuracies = {}
    for tier in Tier:
        tier_correct = sum(1 for r in results if r.tier_results.get(tier) is True)
        tier_accuracies[tier] = tier_correct / total

    return {
        "model": model,
        "puzzle_count": total,
        "solve_pct": solved / total * 100,
        "avg_groups": avg_groups,
        "yellow_pct": tier_accuracies[Tier.YELLOW] * 100,
        "green_pct": tier_accuracies[Tier.GREEN] * 100,
        "blue_pct": tier_accuracies[Tier.BLUE] * 100,
        "purple_pct": tier_accuracies[Tier.PURPLE] * 100,
        "purple_gap": (tier_accuracies[Tier.YELLOW] - tier_accuracies[Tier.PURPLE]) * 100,
    }
