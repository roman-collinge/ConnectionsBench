"""
Loads NYT Connections puzzles from the local JSON dataset and returns validated Puzzle objects.
"""

import json
from pathlib import Path

from src.connectionsbench.models import Puzzle

_DEFAULT_DATA_FILE = Path(__file__).parent.parent.parent / "data" / "connections.json"


def load_all_puzzles(data_file: Path = _DEFAULT_DATA_FILE) -> list[Puzzle]:
    """Load and validate all puzzles from the dataset."""
    if not data_file.exists():
        raise FileNotFoundError(f"Dataset not found: {data_file}")

    with open(data_file) as f:
        json_puzzles = json.load(f)

    return [Puzzle.model_validate(puzzle) for puzzle in json_puzzles]


def load_text_puzzles(data_file: Path = _DEFAULT_DATA_FILE) -> list[Puzzle]:
    """Load all puzzles excluding image-based ones."""
    return [puzzle for puzzle in load_all_puzzles(data_file) if not puzzle.has_images]


def load_puzzle(puzzle_id: int, data_file: Path = _DEFAULT_DATA_FILE) -> Puzzle:
    """Load a single puzzle by ID."""
    puzzles = load_all_puzzles(data_file)
    for puzzle in puzzles:
        if puzzle.id == puzzle_id:
            return puzzle
    raise ValueError(f"Puzzle #{puzzle_id} not found in dataset")
