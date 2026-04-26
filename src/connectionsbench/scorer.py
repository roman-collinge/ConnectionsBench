"""
Scores a model's answer against the correct puzzle solution.
Pure function — no I/O, no API calls.
"""

from src.connectionsbench.models import ModelAnswer, Puzzle, PuzzleResult, Tier


def score_puzzle(puzzle: Puzzle, answer: ModelAnswer, model: str) -> PuzzleResult:
    correct_groups = {frozenset(group.members): group.tier for group in puzzle.groups}

    tier_results: dict[Tier, bool] = {}
    groups_correct = 0

    for proposed in answer.groups:
        proposed_set = frozenset(proposed)
        if proposed_set in correct_groups:
            tier = correct_groups[proposed_set]
            tier_results[tier] = True
            groups_correct += 1

    for group in puzzle.groups:
        if group.tier not in tier_results:
            tier_results[group.tier] = False

    return PuzzleResult(
        puzzle_id=puzzle.id,
        model=model,
        solved=groups_correct == 4,
        groups_correct=groups_correct,
        tier_results=tier_results,
    )
