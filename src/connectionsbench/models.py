"""
Pydantic models for ConnectionsBench.
All data flowing through the benchmark is validated against these models.
"""

from datetime import date
from enum import StrEnum

from pydantic import BaseModel, Field


class Tier(StrEnum):
    YELLOW = "Yellow"
    GREEN = "Green"
    BLUE = "Blue"
    PURPLE = "Purple"


class Group(BaseModel):
    label: str
    tier: Tier
    members: list[str] = Field(min_length=4, max_length=4)


class Puzzle(BaseModel):
    schema_version: int
    id: int
    date: date
    has_images: bool
    words: list[str] = Field(min_length=0, max_length=16)
    groups: list[Group] = Field(min_length=0, max_length=4)


class ModelAnswer(BaseModel):
    """A model's proposed groupings for a puzzle. 4 groups of 4 words."""

    groups: list[list[str]] = Field(min_length=4, max_length=4)


class GroupResult(BaseModel):
    """Scored result for a single proposed group."""

    correct: bool
    # correct results have a tier but incorrect results don't
    tier: Tier | None = None


class PuzzleResult(BaseModel):
    """Full scored result for one puzzle/model run."""

    puzzle_id: int
    model: str
    # ALL groups correct
    solved: bool
    groups_correct: int = Field(ge=0, le=4)
    tier_results: dict[Tier, bool]
