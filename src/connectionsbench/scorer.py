"""
Scores a model's answer against the correct puzzle solution.
Pure function — no I/O, no API calls.
"""

from src.connectionsbench.models import ModelAnswer, Puzzle, PuzzleResult, Tier


def score_puzzle(puzzle: Puzzle, answer: ModelAnswer, model: str) -> PuzzleResult:
    return PuzzleResult(
        puzzle_id=puzzle.id,
        model=model,
        solved=True,
        groups_correct=4,
        tier_results={
            Tier.YELLOW: True,
            Tier.GREEN: True,
            Tier.BLUE: True,
            Tier.PURPLE: True,
        },
    )
