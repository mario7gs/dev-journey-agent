"""Critic schemas: quality audit gate before Step 3."""
from __future__ import annotations

from pydantic import BaseModel, Field


class CriticIssue(BaseModel):
    area: str = Field(min_length=1, max_length=200)
    severity: str = Field(pattern="^(low|medium|high)$")
    message: str = Field(min_length=1, max_length=2000)


class CriticVerdict(BaseModel):
    approved: bool = False
    issues: list[CriticIssue] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)
