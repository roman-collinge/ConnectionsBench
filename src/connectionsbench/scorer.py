"""
Scores a model's answer against the correct puzzle solution.
Pure function — no I/O, no API calls.
"""

from src.connectionsbench.models import ModelAnswer, Puzzle, PuzzleResult, Tier


def score_puzzle(puzzle: Puzzle, answer: ModelAnswer, model: str) -> PuzzleResult:
    correct_groups = {frozenset(group.members) for group in puzzle.groups}

    groups_correct = sum(1 for proposed in answer.groups if frozenset(proposed) in correct_groups)

    return PuzzleResult(
        puzzle_id=puzzle.id,
        model=model,
        solved=groups_correct == 4,
        groups_correct=groups_correct,
        tier_results={
            Tier.YELLOW: True,
            Tier.GREEN: True,
            Tier.BLUE: True,
            Tier.PURPLE: True,
        },
    )
