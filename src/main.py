"""Dev-Journey-Agent CLI — trust-aware feature-planning pipeline.

The default ``blocking`` mode stops before downstream planning when Step 0
contains unresolved questions or high-severity gaps. ``draft`` mode continues
for exploration, but the exported result remains explicitly non-approved.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config.security_guardrails import sanitize_input
from config.settings import Settings, load_settings
from core.checkpoints import (
    CheckpointError,
    build_checkpoint,
    load_resume_point,
    stage_index,
    write_checkpoint,
)
from core.llm_interface import register_mock
from core.memory_manager import append_checkpoint
from core.state import AgentState, ExecutionMode, initial_state
from core.telemetry import TelemetryRecorder
from core.traceability import apply_traceability
from tools.repository_context import RepositoryContextError, build_repository_context

MOCK_DEMO_REFINEMENT = {
    "refined_ticket": "mock: refined ticket — clarify search scope and data source",
    "gaps": [{"area": "scope", "description": "mock gap: undefined search scope", "severity": "high"}],
    "questions": [{"question": "mock: which data source?", "context": "scope"}],
    "assumptions": ["mock: assume public repo, main branch"],
}

MOCK_DEMO_DOD = {
    "contracts": [
        {
            "kind": "json",
            "name": "mock-search-response",
            "schema_ref": "SearchResponse{v1}",
            "status_codes": [200, 400],
        }
    ],
    "dod": [{"criterion": "mock: search returns ranked results", "verifiable": True}],
    "milestones": [
        {"order": 1, "title": "mock: scaffold", "acceptance": "mock: tests pass"},
        {"order": 2, "title": "mock: implement", "acceptance": "mock: DoD verified"},
    ],
}

MOCK_DEMO_SPECS = {
    "prd": {
        "goal": "mock: deliver semantic search over markets",
        "background": "mock: users cannot find markets without exact keywords",
        "users": ["mock: trader"],
        "requirements": ["mock: ranked results", "mock: <600ms p95"],
        "non_goals": ["mock: full-text across docs"],
        "acceptance_criteria": ["mock: top-5 relevant for sample queries"],
    },
    "trd": {
        "components": ["mock: embedder", "mock: vector index", "mock: api"],
        "api_endpoints": [
            {"method": "GET", "path": "/api/search", "description": "mock: semantic search"}
        ],
        "data_model": ["mock: Embedding(query, vector)"],
        "mermaid_flow": "flowchart TD\n    A[Query] --> B[Embed] --> C[Search] --> D[Rank]",
        "security_notes": [],
    },
    "security": {"owasp_checks": [], "input_sanitization": "", "auth_enforcement": ""},
}


def _seed_mocks(ticket: str, demo: bool = False) -> None:
    """Register deterministic fixtures without pretending they are LLM output."""
    if demo:
        register_mock("RefinementOutput", MOCK_DEMO_REFINEMENT)
        register_mock("DoDOutput", MOCK_DEMO_DOD)
        register_mock("SpecsOutput", MOCK_DEMO_SPECS)
        register_mock(
            "TDDOutput",
            {"test_cases": [], "implementation_steps": [], "red_green_notes": "", "coverage_target": 0},
        )
        return

    clean_ticket = sanitize_input(ticket, max_chars=300)
    register_mock(
        "RefinementOutput",
        {
            "refined_ticket": f"Implement and verify: {clean_ticket}",
            "gaps": [],
            "questions": [],
            "assumptions": [
                "Deterministic mock mode; replace with real LLM output for semantic refinement."
            ],
        },
    )
    register_mock(
        "DoDOutput",
        {
            "contracts": [
                {
                    "kind": "json",
                    "name": "feature-response",
                    "schema_ref": "FeatureResponse{v1}",
                    "status_codes": [200, 400],
                }
            ],
            "dod": [
                {
                    "criterion": f"The requested behavior is verifiable: {clean_ticket}",
                    "verifiable": True,
                }
            ],
            "milestones": [
                {
                    "order": 1,
                    "title": "scaffold",
                    "acceptance": "Tests and contract skeleton are in place.",
                },
                {
                    "order": 2,
                    "title": "implement",
                    "acceptance": "Definition of Done is verified.",
                },
            ],
        },
    )
    register_mock(
        "SpecsOutput",
        {
            "prd": {
                "goal": f"Implement: {clean_ticket}",
                "background": "Deterministic mock specification generated without external model calls.",
                "users": ["development team"],
                "requirements": [clean_ticket],
                "non_goals": ["Unrequested production deployment"],
                "acceptance_criteria": [
                    f"The implementation satisfies the requested behavior: {clean_ticket}"
                ],
            },
            "trd": {
                "components": ["application layer", "persistence/integration boundary", "test suite"],
                "api_endpoints": [],
                "data_model": [],
                "mermaid_flow": "flowchart TD\n    A[Request] --> B[Application] --> C[Response]",
                "security_notes": [],
            },
            "security": {"owasp_checks": [], "input_sanitization": "", "auth_enforcement": ""},
        },
    )
    register_mock(
        "TDDOutput",
        {"test_cases": [], "implementation_steps": [], "red_green_notes": "", "coverage_target": 0},
    )


def _refinement_block_reasons(refinement: dict, code_context: dict) -> list[str]:
    reasons: list[str] = []
    for gap in refinement.get("gaps", []) or []:
        if gap.get("severity") == "high":
            reasons.append(
                f"High-severity gap: {gap.get('area', 'unspecified')} — {gap.get('description', '')}"
            )
    for question in refinement.get("questions", []) or []:
        reasons.append(f"Clarification required: {question.get('question', '')}")
    if code_context.get("status") == "error":
        reasons.append(f"Repository context unavailable: {code_context.get('error', '')}")
    return reasons


def _partial_export(state: AgentState, settings: Settings, out_dir: str, summary: str) -> int:
    from tools.html_exporter import write_docs

    state["status"] = "needs_input"
    paths = write_docs(dict(state), out_dir=out_dir)
    append_checkpoint("Pipeline-gate", "needs-input", summary, settings.memory_path)
    print(f"Pipeline stopped: {summary}")
    print(f"Draft clarification report: {paths['md']} + {paths['html']}")
    return 2


def _persist_stage(
    state: AgentState,
    stage: str,
    stage_output: dict,
    run_config: dict,
    settings: Settings,
    audit_step: str,
    audit_status: str,
    audit_summary: str,
) -> None:
    """Write a durable state snapshot, then retain the human audit record."""
    envelope = build_checkpoint(state, stage, stage_output, run_config)
    write_checkpoint(envelope, settings.checkpoint_dir)
    append_checkpoint(audit_step, audit_status, audit_summary, settings.memory_path)


def _exit_code(state: AgentState) -> int:
    return 0 if state.get("status") == "approved" else 2


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dev-Journey-Agent feature-planning pipeline")
    parser.add_argument("--ticket", help="Vague ticket / idea text")
    parser.add_argument("--repo", help="GitHub repo owner/name")
    parser.add_argument("--branch", help="Branch name (default: main)")
    parser.add_argument(
        "--out-dir", help="Export directory for Markdown, HTML, PDF, and case-study files (default: docs)"
    )
    parser.add_argument(
        "--mode",
        choices=("blocking", "draft"),
        help="blocking stops on unresolved Step 0 questions; draft continues but cannot be approved",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Use the fixed semantic-search fixture; useful for demonstrating draft mode",
    )
    parser.add_argument("--resume", metavar="RUN_ID", help="Resume a durable checkpoint run")
    args = parser.parse_args(argv)
    if not args.resume and not args.ticket:
        parser.error("--ticket is required unless --resume is supplied")
    if args.resume and args.demo:
        parser.error("--demo is recorded in the run configuration; omit it when resuming")
    if args.resume and args.out_dir:
        parser.error("--out-dir is recorded in the run configuration; omit it when resuming")
    return args


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    settings = load_settings()
    from agents.critic_agent import run as run_critic
    from agents.dod_agent import run as run_dod
    from agents.refinement_agent import run as run_refine
    from agents.specs_agent import run as run_specs
    from agents.tdd_agent import run as run_tdd

    if args.resume:
        try:
            checkpoint = load_resume_point(settings.checkpoint_dir, args.resume)
        except CheckpointError as exc:
            raise SystemExit(f"Cannot resume run {args.resume}: {exc}") from exc
        state = AgentState(checkpoint.state)
        run_config = checkpoint.run_config
        if args.mode and args.mode != checkpoint.mode:
            raise SystemExit("--mode must match the checkpointed execution mode")
        if args.ticket and args.ticket != state["ticket_text"]:
            raise SystemExit("--ticket must match the checkpointed ticket")
        if args.repo is not None and args.repo != state["repo_ref"]:
            raise SystemExit("--repo must match the checkpointed repository")
        if args.branch is not None and args.branch != state["branch"]:
            raise SystemExit("--branch must match the checkpointed branch")
        if run_config.get("use_mock_llm") != settings.use_mock_llm:
            raise SystemExit("USE_MOCK_LLM must match the checkpointed run configuration")
        completed_stage = checkpoint.stage
        out_dir = str(run_config["out_dir"])
        demo = bool(run_config.get("demo", False))
        print(f"Resuming run {state['run_id']} after {completed_stage}.")
    else:
        if args.demo and not settings.use_mock_llm:
            raise SystemExit("--demo requires USE_MOCK_LLM=true")
        mode: ExecutionMode = args.mode or "blocking"
        state = initial_state(args.ticket or "", args.repo or "", args.branch or "main", mode=mode)
        state["run_id"] = uuid4().hex
        run_config = {
            "demo": args.demo,
            "out_dir": args.out_dir or "docs",
            "use_mock_llm": settings.use_mock_llm,
        }
        completed_stage = ""
        out_dir = str(run_config["out_dir"])
        demo = args.demo

    if settings.use_mock_llm:
        _seed_mocks(state["ticket_text"], demo=demo)

    mode = state["mode"]
    telemetry = TelemetryRecorder(
        settings,
        run_id=state["run_id"],
        mode=mode,
        state_provider=lambda: dict(state),
    )
    if args.resume:
        telemetry.record_event("resume", resumed_from=completed_stage)
    completed_index = stage_index(completed_stage) if completed_stage else 0

    if completed_index < stage_index("repository_context"):
        with telemetry.stage("repository_context"):
            try:
                state["code_context"] = build_repository_context(
                    state["repo_ref"],
                    branch=state["branch"],
                    token=settings.github_token,
                    budget_tokens=settings.repo_context_budget_tokens,
                    max_files=settings.repo_context_max_files,
                )
            except RepositoryContextError as exc:
                state["code_context"] = {
                    "status": "error",
                    "error": str(exc),
                    "repo_ref": state["repo_ref"],
                    "branch": state["branch"],
                }
                state["errors"] = [str(exc)]
                telemetry.mark_current("error", error_type=type(exc).__name__)
        _persist_stage(
            state,
            "repository_context",
            state["code_context"],
            run_config,
            settings,
            "Repository-context",
            "done" if state["code_context"].get("status") != "error" else "error",
            str(state["code_context"].get("status", "unknown")),
        )
        completed_index = stage_index("repository_context")

    if state["code_context"].get("status") == "error" and mode == "blocking":
        reason = str(state["code_context"].get("error", ""))
        telemetry.record_event("pipeline_gate", status="needs_input", block_reasons=[reason])
        return _partial_export(state, settings, out_dir, reason)
    if state["code_context"].get("status") == "error":
        print("Warning: continuing in draft mode without repository context.")

    if completed_index < stage_index("refinement"):
        with telemetry.stage("refinement"):
            patch0, refinement = run_refine(state, use_mock=settings.use_mock_llm)
            state.update(patch0)
            state["block_reasons"] = _refinement_block_reasons(
                dict(refinement.model_dump()), state["code_context"]
            )
        _persist_stage(
            state,
            "refinement",
            state["refinement"],
            run_config,
            settings,
            "Step0-refinement",
            "done",
            refinement.refined_ticket[:500],
        )
        completed_index = stage_index("refinement")

    block_reasons = list(state.get("block_reasons", []))
    if block_reasons and mode == "blocking":
        telemetry.record_event("pipeline_gate", status="needs_input", block_reasons=block_reasons)
        return _partial_export(state, settings, out_dir, " | ".join(block_reasons))
    if block_reasons and completed_index == stage_index("refinement"):
        print("Draft mode: continuing with unresolved input:")
        for reason in block_reasons:
            print(f" - {reason}")

    if completed_index < stage_index("dod"):
        with telemetry.stage("dod"):
            patch1, dod = run_dod(state, use_mock=settings.use_mock_llm)
            state.update(patch1)
        _persist_stage(
            state,
            "dod",
            state["dod"],
            run_config,
            settings,
            "Step1-dod",
            "done",
            f"{len(dod.contracts)} contracts, {len(dod.dod)} DoD items, {len(dod.milestones)} milestones",
        )
        completed_index = stage_index("dod")

    if completed_index < stage_index("specs"):
        with telemetry.stage("specs"):
            patch2, specs = run_specs(state, use_mock=settings.use_mock_llm)
            state.update(patch2)
            state.update(apply_traceability(state))
        _persist_stage(
            state,
            "specs",
            state["specs"],
            run_config,
            settings,
            "Step2-specs",
            "done",
            f"PRD goal: {specs.prd.goal[:200]} | {len(specs.trd.components)} components, {len(specs.security.owasp_checks)} OWASP checks",
        )
        completed_index = stage_index("specs")

    if completed_index < stage_index("critic_pre_tdd"):
        with telemetry.stage("critic_pre_tdd"):
            patch_c, verdict = run_critic(state, use_mock=settings.use_mock_llm)
            state.update(patch_c)
            if not verdict.approved and mode == "blocking":
                state["block_reasons"] = [*state.get("block_reasons", []), *verdict.missing]
        _persist_stage(
            state,
            "critic_pre_tdd",
            state["critic_verdict"],
            run_config,
            settings,
            "Critic-gate",
            "approved" if verdict.approved else "needs-attention",
            f"approved={verdict.approved} missing={verdict.missing} issues={[i.message for i in verdict.issues[:5]]}",
        )
        completed_index = stage_index("critic_pre_tdd")

    verdict_data = state.get("critic_verdict", {})
    if not verdict_data.get("approved", False) and mode == "blocking":
        telemetry.record_event(
            "pipeline_gate", status="needs_input", block_reasons=list(state.get("block_reasons", []))
        )
        return _partial_export(state, settings, out_dir, "Critic gate requires attention")

    if completed_index < stage_index("tdd"):
        with telemetry.stage("tdd"):
            patch3, tdd = run_tdd(state, use_mock=settings.use_mock_llm)
            state.update(patch3)
            state.update(apply_traceability(state))
            kinds = {case.kind for case in tdd.test_cases}
        _persist_stage(
            state,
            "tdd",
            state["tdd"],
            run_config,
            settings,
            "Step3-tdd",
            "done",
            f"{len(tdd.test_cases)} tests (unit={'unit' in kinds}, integration={'integration' in kinds}), {len(tdd.implementation_steps)} steps, coverage>={tdd.coverage_target}%",
        )
        completed_index = stage_index("tdd")

    if completed_index < stage_index("critic_final"):
        with telemetry.stage("critic_final"):
            patch_c_final, verdict = run_critic(state, use_mock=settings.use_mock_llm)
            state.update(patch_c_final)
            state["status"] = "draft" if block_reasons else ("approved" if verdict.approved else "needs_input")
        _persist_stage(
            state,
            "critic_final",
            state["critic_verdict"],
            run_config,
            settings,
            "Critic-final",
            "approved" if verdict.approved else "needs-attention",
            f"approved={verdict.approved} missing={verdict.missing}",
        )
        completed_index = stage_index("critic_final")

    if completed_index < stage_index("export"):
        from tools.html_exporter import write_docs

        with telemetry.stage("export"):
            paths = write_docs(
                dict(state), out_dir=out_dir, include_pdf=True, include_presentation=True
            )
        _persist_stage(
            state,
            "export",
            paths,
            run_config,
            settings,
            "Step4-export",
            "done",
            "wrote " + " + ".join(
                str(paths[key])
                for key in ("md", "html", "pdf", "presentation", "presentation_pdf")
                if key in paths
            ),
        )
        output_paths = " + ".join(
            str(paths[key])
            for key in ("md", "html", "pdf", "presentation", "presentation_pdf")
            if key in paths
        )
        print(f"Step 4: wrote {output_paths} ({state['status']}).")
        for key in ("pdf_error", "presentation_pdf_error"):
            if key in paths:
                print(f"Warning: {paths[key]}")
    else:
        print(f"Run {state['run_id']} is already complete ({state['status']}).")
    return _exit_code(state)


if __name__ == "__main__":
    raise SystemExit(main())
