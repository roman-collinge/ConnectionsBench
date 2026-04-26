"""
Tests for models.py
"""

from datetime import date

import pytest
from pydantic import ValidationError

from src.connectionsbench.models import Group, GroupResult, ModelAnswer, Puzzle, PuzzleResult, Tier

# Tier tests


def test_tier_values():
    assert Tier.YELLOW == "Yellow"
    assert Tier.GREEN == "Green"
    assert Tier.BLUE == "Blue"
    assert Tier.PURPLE == "Purple"


# Group Tests


def test_group_valid():
    group = Group(label="TEST GROUP", tier=Tier.YELLOW, members=["A", "B", "C", "D"])
    assert group.label == "TEST GROUP"
    assert group.tier == Tier.YELLOW
    assert group.members == ["A", "B", "C", "D"]


def test_group_rejects_wrong_member_count():
    with pytest.raises(ValidationError):
        Group(label="TEST GROUP", tier=Tier.YELLOW, members=["A", "B", "C"])


def test_group_rejects_too_many_members():
    with pytest.raises(ValidationError):
        Group(label="TEST GROUP", tier=Tier.YELLOW, members=["A", "B", "C", "D", "E"])


def test_group_accepts_tier_from_string():
    group = Group(label="TEST GROUP", tier="Yellow", members=["A", "B", "C", "D"])
    assert group.tier == Tier.YELLOW


# Puzzle tests


def test_puzzle_valid():
    puzzle = Puzzle(
        schema_version=1,
        id=1,
        date="2023-06-12",
        has_images=False,
        words=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"],
        groups=[
            Group(label="G1", tier=Tier.YELLOW, members=["A", "B", "C", "D"]),
            Group(label="G2", tier=Tier.GREEN, members=["E", "F", "G", "H"]),
            Group(label="G3", tier=Tier.BLUE, members=["I", "J", "K", "L"]),
            Group(label="G4", tier=Tier.PURPLE, members=["M", "N", "O", "P"]),
        ],
    )
    assert puzzle.id == 1
    assert puzzle.date == date(2023, 6, 12)
    assert puzzle.has_images is False
    assert len(puzzle.words) == 16
    assert len(puzzle.groups) == 4


def test_puzzle_date_parsed_from_string():
    puzzle = Puzzle(schema_version=1, id=1, date="2024-01-15", has_images=False, words=[], groups=[])
    assert puzzle.date == date(2024, 1, 15)


def test_puzzle_allows_empty_words_and_groups_for_image_puzzle():
    puzzle = Puzzle(schema_version=1, id=1, date="2023-06-12", has_images=True, words=[], groups=[])
    assert puzzle.words == []
    assert puzzle.groups == []


def test_puzzle_rejects_too_many_words():
    with pytest.raises(ValidationError):
        Puzzle(schema_version=1, id=1, date="2023-06-12", has_images=False, words=["A"] * 17, groups=[])


def test_puzzle_rejects_too_many_groups():
    with pytest.raises(ValidationError):
        Puzzle(
            schema_version=1,
            id=1,
            date="2023-06-12",
            has_images=False,
            words=[],
            groups=[Group(label=f"G{i}", tier=Tier.YELLOW, members=["A", "B", "C", "D"]) for i in range(5)],
        )


# ModelAnswer tests


def test_model_answer_valid():
    answer = ModelAnswer(
        groups=[
            ["A", "B", "C", "D"],
            ["E", "F", "G", "H"],
            ["I", "J", "K", "L"],
            ["M", "N", "O", "P"],
        ]
    )
    assert len(answer.groups) == 4


def test_model_answer_rejects_wrong_group_count():
    with pytest.raises(ValidationError):
        ModelAnswer(groups=[["A", "B", "C", "D"]])


# GroupResult tests


def test_group_result_correct():
    result = GroupResult(correct=True, tier=Tier.YELLOW)
    assert result.correct is True
    assert result.tier == Tier.YELLOW


def test_group_result_incorrect_has_no_tier():
    result = GroupResult(correct=False)
    assert result.correct is False
    assert result.tier is None


# PuzzleResult tests


def test_puzzle_result_valid():
    result = PuzzleResult(
        puzzle_id=1,
        model="claude-sonnet-4-5",
        solved=True,
        groups_correct=4,
        tier_results={
            Tier.YELLOW: True,
            Tier.GREEN: True,
            Tier.BLUE: True,
            Tier.PURPLE: True,
        },
    )
    assert result.solved is True
    assert result.groups_correct == 4


def test_puzzle_result_rejects_invalid_groups_correct():
    with pytest.raises(ValidationError):
        PuzzleResult(puzzle_id=1, model="claude-sonnet-4-5", solved=False, groups_correct=5, tier_results={})


def test_puzzle_result_partial():
    result = PuzzleResult(
        puzzle_id=1,
        model="gpt-4o",
        solved=False,
        groups_correct=2,
        tier_results={
            Tier.YELLOW: True,
            Tier.GREEN: True,
            Tier.BLUE: False,
            Tier.PURPLE: False,
        },
    )
    assert result.solved is False
    assert result.groups_correct == 2
    assert result.tier_results[Tier.PURPLE] is False
