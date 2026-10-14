"""Step 2 schemas: PRD/TRD + Mermaid flow + security assessment."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field, model_validator


class RequirementItem(BaseModel):
    id: str = Field(default="", max_length=40)
    text: str = Field(min_length=1, max_length=2000)
    priority: str = Field(default="P1", pattern="^(P0|P1|P2)$")

    @model_validator(mode="before")
    @classmethod
    def coerce_legacy_string(cls, value: Any) -> Any:
        if isinstance(value, str):
            return {"text": value}
        return value


class AcceptanceCriterion(BaseModel):
    id: str = Field(default="", max_length=40)
    text: str = Field(min_length=1, max_length=2000)
    requirement_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def coerce_legacy_string(cls, value: Any) -> Any:
        if isinstance(value, str):
            return {"text": value}
        return value


class PRDSpec(BaseModel):
    goal: str = Field(min_length=1, max_length=2000)
    background: str = Field(default="", max_length=2000)
    users: list[str] = Field(default_factory=list)
    requirements: list[RequirementItem] = Field(default_factory=list)
    non_goals: list[str] = Field(default_factory=list)
    acceptance_criteria: list[AcceptanceCriterion] = Field(default_factory=list)


class APIEndpoint(BaseModel):
    method: str = Field(pattern="^(GET|POST|PUT|PATCH|DELETE)$")
    path: str = Field(min_length=1, max_length=500)
    description: str = Field(default="", max_length=1000)


class OWASPCheck(BaseModel):
    id: str = Field(default="", max_length=40)
    check: str = Field(min_length=1, max_length=300)
    status: str = Field(pattern="^(pass|fail|n/a)$")
    notes: str = Field(default="", max_length=1000)


class SecurityAssessment(BaseModel):
    owasp_checks: list[OWASPCheck] = Field(default_factory=list)
    input_sanitization: str = Field(default="", max_length=2000)
    auth_enforcement: str = Field(default="", max_length=2000)


class TRDSpec(BaseModel):
    components: list[str] = Field(default_factory=list)
    api_endpoints: list[APIEndpoint] = Field(default_factory=list)
    data_model: list[str] = Field(default_factory=list)
    mermaid_flow: str = Field(default="", max_length=10000)
    security_notes: list[str] = Field(default_factory=list)


class SpecsOutput(BaseModel):
    prd: PRDSpec
    trd: TRDSpec
    security: SecurityAssessment = Field(default_factory=SecurityAssessment)
