"""Step 3 schemas: TDD suite (Red-Green) + implementation roadmap."""
from __future__ import annotations

from pydantic import BaseModel, Field


class TestCase(BaseModel):
    id: str = Field(default="", max_length=40)
    name: str = Field(min_length=1, max_length=300)
    kind: str = Field(pattern="^(unit|integration|e2e)$")
    file: str = Field(default="", max_length=500)
    description: str = Field(min_length=1, max_length=2000)
    covers: list[str] = Field(default_factory=list)
    requirement_ids: list[str] = Field(default_factory=list)
    contract_ids: list[str] = Field(default_factory=list)
    acceptance_criteria_ids: list[str] = Field(default_factory=list)
    priority: str = Field(default="P1", pattern="^(P0|P1|P2)$")


class ImplementationStep(BaseModel):
    id: str = Field(default="", max_length=40)
    order: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=300)
    detail: str = Field(default="", max_length=2000)
    tests: list[str] = Field(default_factory=list)
    test_ids: list[str] = Field(default_factory=list)
    requirement_ids: list[str] = Field(default_factory=list)
    files: list[str] = Field(default_factory=list)


class TDDOutput(BaseModel):
    test_cases: list[TestCase] = Field(default_factory=list)
    implementation_steps: list[ImplementationStep] = Field(default_factory=list)
    red_green_notes: str = Field(default="", max_length=3000)
    coverage_target: int = Field(default=80, ge=0, le=100)
