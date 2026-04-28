"""
Tests for runner.py
Mocks PydanticAI agent to avoid real API calls in test suite.
"""

from datetime import date
from src.connectionsbench.models import Group, Puzzle, Tier
from src.connectionsbench.runner import build_prompt

PUZZLE = Puzzle(
    schema_version=1,
    id=1,
    date=date(2023, 6, 12),
    has_images=False,
    words=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"],
    groups=[
        Group(label="G1", tier=Tier.YELLOW, members=["A", "B", "C", "D"]),
        Group(label="G2", tier=Tier.GREEN, members=["E", "F", "G", "H"]),
        Group(label="G3", tier=Tier.BLUE, members=["I", "J", "K", "L"]),
        Group(label="G4", tier=Tier.PURPLE, members=["M", "N", "O", "P"]),
    ],
)


# build_prompt tests


def test_build_prompt_contains_all_words():
    prompt = build_prompt(PUZZLE)
    for word in PUZZLE.words:
        assert word in prompt
