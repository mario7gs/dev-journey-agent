"""Step 0: Context-Aware Refinement & Code Filtering.

LangGraph-ready signature: run(state) -> (patch, RefinementOutput).
"""
from __future__ import annotations

from typing import Any

from config.security_guardrails import sanitize_input
from core.llm_interface import generate_structured
from core.state import AgentState
from schemas.step0_refinement import RefinementOutput


def build_prompt(ticket: str, code_context: dict[str, Any]) -> str:
    chunks = code_context.get("chunks", [])
    ctx_lines = "\n".join(f"- {c.get('path')}: {c.get('summary')}" for c in chunks[:30])
    return (
        "Refine the ticket given code context.\n"
        f"Ticket: {ticket}\n"
        f"Repository context status: {code_context.get('status', 'not_provided')}\n"
        f"Repository: {code_context.get('repo_ref', '')}@{code_context.get('branch', '')}\n"
        f"Code context:\n{ctx_lines or '(no repository context available)'}\n"
        "Return gaps, clarifying questions, assumptions, refined_ticket."
    )


def run(state: AgentState, use_mock: bool = True) -> tuple[dict[str, Any], RefinementOutput]:
    ticket = sanitize_input(str(state.get("ticket_text", "")))
    if not ticket:
        raise ValueError("ticket_text is required")
    code_context = dict(state.get("code_context", {}))
    prompt = build_prompt(ticket, code_context)
    output = generate_structured(prompt, RefinementOutput, use_mock=use_mock)
    patch = {"refinement": output.model_dump()}
    return patch, output
