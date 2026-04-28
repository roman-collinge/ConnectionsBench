import random

from pydantic_ai import Agent

from src.connectionsbench.models import Puzzle, ModelAnswer

_PROMPT_TEMPLATE = """You are solving a NYT Connections puzzle.

You will be given 16 words. Your task is to group them into exactly 4 groups of 4 words,
where each group shares a common connection.

Rules:
- Every word must be used exactly once
- Each group contains exactly 4 words
- No word can appear in more than one group

Words: {words}

Return your answer as 4 groups of 4 words. Do not include explanations or labels."""


def build_prompt(puzzle: Puzzle) -> str:
    """Build the prompt for a puzzle, shuffling words to prevent position bias."""
    if puzzle.has_images:
        raise ValueError(f"Cannot run image puzzle #{puzzle.id}")
    words = puzzle.words.copy()
    random.shuffle(words)
    return _PROMPT_TEMPLATE.format(words=", ".join(words))


def run_puzzle(puzzle: Puzzle, model: str) -> ModelAnswer:
    agent = Agent(model, result_type=ModelAnswer)
    result = agent.run_sync("")
    return result.data
