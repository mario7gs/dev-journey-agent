"""AgentState — single shared state shape.

Designed to be LangGraph-compatible: future graph nodes take
AgentState and return a patch dict. The plain-pipeline orchestrator
in main.py uses the same contract today.
"""
from __future__ import annotations

from typing import Any, Literal, TypedDict

ExecutionMode = Literal["blocking", "draft"]
RunStatus = Literal["running", "needs_input", "draft", "approved", "failed"]


class AgentState(TypedDict, total=False):
    run_id: str
    mode: ExecutionMode
    status: RunStatus
    ticket_text: str
    repo_ref: str
    branch: str
    code_context: dict[str, Any]
    block_reasons: list[str]
    errors: list[str]
    refinement: dict[str, Any]
    dod: dict[str, Any]
    specs: dict[str, Any]
    tdd: dict[str, Any]
    critic_verdict: dict[str, Any]


def initial_state(
    ticket_text: str,
    repo_ref: str = "",
    branch: str = "main",
    mode: ExecutionMode = "blocking",
) -> AgentState:
    if mode not in ("blocking", "draft"):
        raise ValueError(f"Unsupported execution mode: {mode}")
    return {
        "run_id": "",
        "mode": mode,
        "status": "running",
        "ticket_text": ticket_text,
        "repo_ref": repo_ref,
        "branch": branch,
        "code_context": {},
        "block_reasons": [],
        "errors": [],
        "refinement": {},
        "dod": {},
        "specs": {},
        "tdd": {},
        "critic_verdict": {},
    }
