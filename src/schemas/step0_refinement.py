"""Step 0 schemas: gap analysis + human-in-the-loop questions."""
from __future__ import annotations

from pydantic import BaseModel, Field


class GapItem(BaseModel):
    area: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    severity: str = Field(pattern="^(low|medium|high)$")


class ClarifyingQuestion(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    context: str = Field(default="", max_length=1000)


class RefinementOutput(BaseModel):
    refined_ticket: str = Field(min_length=1, max_length=10000)
    gaps: list[GapItem] = Field(default_factory=list)
    questions: list[ClarifyingQuestion] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
