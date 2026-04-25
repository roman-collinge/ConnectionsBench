"""
Tests for loader.py
"""

import json
from pathlib import Path

import pytest

from src.connectionsbench.loader import load_all_puzzles, load_puzzle, load_text_puzzles
from src.connectionsbench.models import Puzzle, Tier

MOCK_PUZZLES = [
    {
        "schema_version": 1,
        "id": 1,
        "date": "2023-06-12",
        "has_images": False,
        "words": ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"],
        "groups": [
            {"label": "G1", "tier": "Yellow", "members": ["A", "B", "C", "D"]},
            {"label": "G2", "tier": "Green", "members": ["E", "F", "G", "H"]},
            {"label": "G3", "tier": "Blue", "members": ["I", "J", "K", "L"]},
            {"label": "G4", "tier": "Purple", "members": ["M", "N", "O", "P"]},
        ],
    },
    {
        "schema_version": 1,
        "id": 2,
        "date": "2023-06-13",
        "has_images": True,
        "words": [],
        "groups": [],
    },
    {
        "schema_version": 1,
        "id": 3,
        "date": "2023-06-14",
        "has_images": False,
        "words": ["Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", "AA", "BB", "CC", "DD", "EE", "FF"],
        "groups": [
            {"label": "G1", "tier": "Yellow", "members": ["Q", "R", "S", "T"]},
            {"label": "G2", "tier": "Green", "members": ["U", "V", "W", "X"]},
            {"label": "G3", "tier": "Blue", "members": ["Y", "Z", "AA", "BB"]},
            {"label": "G4", "tier": "Purple", "members": ["CC", "DD", "EE", "FF"]},
        ],
    },
]


# Setup mock dataset for tests
@pytest.fixture
def dataset(tmp_path):
    data_file = tmp_path / "connections.json"
    data_file.write_text(json.dumps(MOCK_PUZZLES))
    return data_file


# Test load_all_puzzles()


def test_load_all_puzzles_returns_all(dataset):
    puzzles = load_all_puzzles(dataset)
    assert len(puzzles) == 3


def test_load_all_puzzles_returns_puzzle_objects(dataset):
    puzzles = load_all_puzzles(dataset)
    assert all(isinstance(p, Puzzle) for p in puzzles)


def test_load_all_puzzles_raises_when_file_missing():
    with pytest.raises(FileNotFoundError):
        load_all_puzzles(Path("/nonexistent/connections.json"))


def test_load_all_puzzles_validates_tiers(dataset):
    puzzles = load_all_puzzles(dataset)
    assert puzzles[0].groups[0].tier == Tier.YELLOW
    assert puzzles[0].groups[3].tier == Tier.PURPLE


# Test load_text_puzzles()


def test_load_text_puzzles_excludes_image_puzzles(dataset):
    puzzles = load_text_puzzles(dataset)
    assert len(puzzles) == 2


def test_load_text_puzzles_returns_only_text(dataset):
    puzzles = load_text_puzzles(dataset)
    assert all(not p.has_images for p in puzzles)


# Test load_puzzle()


def test_load_puzzle_returns_correct_puzzle(dataset):
    puzzle = load_puzzle(1, dataset)
    assert puzzle.id == 1


def test_load_puzzle_raises_on_missing_id(dataset):
    with pytest.raises(ValueError, match="Puzzle #99 not found"):
        load_puzzle(99, dataset)


def test_load_puzzle_returns_puzzle_object(dataset):
    puzzle = load_puzzle(1, dataset)
    assert isinstance(puzzle, Puzzle)
