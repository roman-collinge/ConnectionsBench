"""
Scores a model's answer against the correct puzzle solution.
Pure function — no I/O, no API calls.
"""

from src.connectionsbench.models import ModelAnswer, Puzzle, PuzzleResult, Tier


def score_puzzle(puzzle: Puzzle, answer: ModelAnswer, model: str) -> PuzzleResult:
    # No point trying to score images
    if puzzle.has_images:
        raise ValueError(f"Cannot score image puzzle #{puzzle.id}")

    # frozenset required for dict keys and order independence
    correct_groups = {frozenset(group.members): group.tier for group in puzzle.groups}

    tier_results: dict[Tier, bool] = {}
    groups_correct = 0
    # Track matched groups to prevent duplicate proposed groups scoring twice
    matched: set[frozenset] = set()

    # Score each proposed group against the correct groups
    for proposed in answer.groups:
        proposed_set = frozenset(proposed)
        if proposed_set in correct_groups and proposed_set not in matched:
            tier = correct_groups[proposed_set]
            tier_results[tier] = True
            groups_correct += 1
            matched.add(proposed_set)

    # Any tier not matched by a correct proposal is marked False
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
