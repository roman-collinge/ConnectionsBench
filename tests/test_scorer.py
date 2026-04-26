"""
Tests for scorer.py
"""

from datetime import date
from src.connectionsbench.models import Group, ModelAnswer, Puzzle, Tier
from src.connectionsbench.scorer import score_puzzle

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


def test_score_all_correct():
    answer = ModelAnswer(
        groups=[
            ["A", "B", "C", "D"],
            ["E", "F", "G", "H"],
            ["I", "J", "K", "L"],
            ["M", "N", "O", "P"],
        ]
    )
    result = score_puzzle(PUZZLE, answer, model="test-model")
    assert result.solved is True
    assert result.groups_correct == 4


def test_score_none_correct():
    answer = ModelAnswer(
        groups=[
            ["A", "B", "C", "E"],
            ["D", "F", "G", "H"],
            ["I", "J", "K", "M"],
            ["L", "N", "O", "P"],
        ]
    )
    result = score_puzzle(PUZZLE, answer, model="test-model")
    assert result.solved is False
    assert result.groups_correct == 0


def test_score_tier_results_all_correct():
    answer = ModelAnswer(
        groups=[
            ["A", "B", "C", "D"],
            ["E", "F", "G", "H"],
            ["I", "J", "K", "L"],
            ["M", "N", "O", "P"],
        ]
    )
    result = score_puzzle(PUZZLE, answer, model="test-model")
    assert result.tier_results[Tier.YELLOW] is True
    assert result.tier_results[Tier.GREEN] is True
    assert result.tier_results[Tier.BLUE] is True
    assert result.tier_results[Tier.PURPLE] is True


def test_score_tier_results_partial():
    answer = ModelAnswer(
        groups=[
            ["A", "B", "C", "D"],
            ["E", "F", "G", "H"],
            ["I", "J", "K", "M"],
            ["L", "N", "O", "P"],
        ]
    )
    result = score_puzzle(PUZZLE, answer, model="test-model")
    assert result.tier_results[Tier.YELLOW] is True
    assert result.tier_results[Tier.GREEN] is True
    assert result.tier_results[Tier.BLUE] is False
    assert result.tier_results[Tier.PURPLE] is False
