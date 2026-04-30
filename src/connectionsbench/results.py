"""
Results loading and leaderboard calculation for ConnectionsBench.
"""

from pathlib import Path

from src.connectionsbench.models import PuzzleResult

_DEFAULT_RESULTS_DIR = Path(__file__).parent.parent.parent / "results"


def load_results():
    pass


def save_result(result: PuzzleResult, model: str, results_dir: Path = _DEFAULT_RESULTS_DIR) -> None:
    """Append a single PuzzleResult to the model's JSONL file."""
    results_dir.mkdir(parents=True, exist_ok=True)
    path = results_dir / f"{model.replace(':', '_')}.jsonl"
    with open(path, "a") as f:
        f.write(result.model_dump_json() + "\n")


def get_run_puzzle_ids():
    pass


def check_duplicate_run():
    pass


def calculate_leaderboard():
    pass


def calculate_model_metrics():
    pass
