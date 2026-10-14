"""Step 1 schemas: output contracts, DoD, milestones."""
from __future__ import annotations

from pydantic import BaseModel, Field


class OutputContract(BaseModel):
    id: str = Field(default="", max_length=40)
    kind: str = Field(pattern="^(json|db|http)$")
    name: str = Field(min_length=1, max_length=200)
    schema_ref: str = Field(min_length=1, max_length=1000)
    status_codes: list[int] = Field(default_factory=list)
    requirement_ids: list[str] = Field(default_factory=list)


class DoDItem(BaseModel):
    id: str = Field(default="", max_length=40)
    criterion: str = Field(min_length=1, max_length=1000)
    verifiable: bool = True
    requirement_ids: list[str] = Field(default_factory=list)
    contract_ids: list[str] = Field(default_factory=list)


class Milestone(BaseModel):
    id: str = Field(default="", max_length=40)
    order: int = Field(ge=1)
    title: str = Field(min_length=1, max_length=300)
    acceptance: str = Field(min_length=1, max_length=2000)
    requirement_ids: list[str] = Field(default_factory=list)
    contract_ids: list[str] = Field(default_factory=list)


class DoDOutput(BaseModel):
    contracts: list[OutputContract] = Field(min_length=1)
    dod: list[DoDItem] = Field(min_length=1)
    milestones: list[Milestone] = Field(min_length=1)
