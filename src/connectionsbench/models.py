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
