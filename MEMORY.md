# MEMORY.md — Dev-Journey-Agent checkpoint log
# Append-only. Each step appends one line/block. Never rewrite history.

<!-- checkpoints below -->

## [2026-10-14T16:30:00+02:00] Phase 3 — review and team signals
Implemented machine-readable `run-status.json` payloads and a separate
GitHub review-signals job. The workflow publishes the `dev-journey/plan`
commit status for approved, draft, and needs-input outcomes and supports
explicitly opt-in issue or pull-request comments. The planning job remains
`contents: read`; review signals use only status and issue-comment permissions.
No source-code edits, merges, or deployments are performed by the action.

## [2026-10-14T16:00:00+02:00] GitHub-agent handoff — resumed
The private repository `mario7gs/dev-journey-agent` is connected and uses the
`main` default branch. Baseline commit `c5cea69`, CI workflow commit
`3dcc981`, and packaging/documentation commit `bcbcd04` are published. The
manual planning action was added as connector commit `4fe71e6` because the
available Git push token lacks the `workflow` scope. The release matrix passed
with expected exit codes 2 (blocked), 2 (draft), 0 (normal), and 0 (resumed).
Release tag `v0.1.0` is published; the GitHub-native queue is complete.

## [2026-10-14T17:00:00+02:00] Phase 4 — security and persistence foundations
Added recursive credential redaction for checkpoints, memory, telemetry, and
Phoenix attributes. Added configurable per-run token/cost budgets and a local
telemetry byte cap. The GitHub workflow now persists redacted checkpoints,
memory, telemetry, and cost summaries as a 14-day artifact. CI now runs a
recognizable-secret audit, provider usage reports expose budget status, and
local checkpoint pruning is explicit and dry-run by default. Phase 4 is
complete.

## [2026-10-12T22:50:00+02:00] GitHub-agent handoff — scheduled
The GitHub plugin is authenticated for repository read access, but no
repository-creation operation is exposed. The target private repository does
not exist yet. Resume from the **Next-session queue** in
`docs/MVP/GITHUB_AGENT_ROADMAP.html`: create the empty private repository,
configure a local Git author identity, commit the baseline, populate the
repository, package the CLI, add the manual workflow, and run the release
verification matrix. No credentials are stored in this project.

## [2026-10-07T20:44:37+00:00] Step0-refinement — done
mock: refined ticket — clarify search scope and data source

## [2026-10-07T20:44:37+00:00] Step1-dod — done
1 contracts, 7 DoD items, 2 milestones

## [2026-10-07T20:45:26+00:00] Step0-refinement — done
mock: refined ticket — clarify search scope and data source

## [2026-10-07T20:45:26+00:00] Step1-dod — done
1 contracts, 7 DoD items, 2 milestones

## [2026-10-07T20:48:01+00:00] Step0-refinement — done
mock: refined ticket — clarify search scope and data source

## [2026-10-07T20:48:01+00:00] Step1-dod — done
1 contracts, 7 DoD items, 2 milestones

## [2026-10-07T20:48:01+00:00] Step2-specs — done
PRD goal: mock: deliver semantic search over markets | 3 components, 5 OWASP checks

## [2026-10-07T20:48:01+00:00] Critic-gate — approved
approved=True missing=[] issues=[]

## [2026-10-07T20:53:08+00:00] Step0-refinement — done
mock: refined ticket — clarify search scope and data source

## [2026-10-07T20:53:08+00:00] Step1-dod — done
1 contracts, 7 DoD items, 2 milestones

## [2026-10-07T20:53:08+00:00] Step2-specs — done
PRD goal: mock: deliver semantic search over markets | 3 components, 5 OWASP checks

## [2026-10-07T20:53:08+00:00] Critic-gate — approved
approved=True missing=[] issues=[]

## [2026-10-07T20:53:08+00:00] Step3-tdd — done
2 tests (unit=True, integration=True), 2 steps, coverage>=80%

## [2026-10-07T20:55:06+00:00] Step0-refinement — done
mock: refined ticket — clarify search scope and data source

## [2026-10-07T20:55:06+00:00] Step1-dod — done
1 contracts, 7 DoD items, 2 milestones

## [2026-10-07T20:55:06+00:00] Step2-specs — done
PRD goal: mock: deliver semantic search over markets | 3 components, 5 OWASP checks

## [2026-10-07T20:55:06+00:00] Critic-gate — approved
approved=True missing=[] issues=[]

## [2026-10-07T20:55:06+00:00] Step3-tdd — done
2 tests (unit=True, integration=True), 2 steps, coverage>=80%

## [2026-10-07T20:55:16+00:00] Step0-refinement — done
mock: refined ticket — clarify search scope and data source

## [2026-10-07T20:55:16+00:00] Step1-dod — done
1 contracts, 7 DoD items, 2 milestones

## [2026-10-07T20:55:16+00:00] Step2-specs — done
PRD goal: mock: deliver semantic search over markets | 3 components, 5 OWASP checks

## [2026-10-07T20:55:16+00:00] Critic-gate — approved
approved=True missing=[] issues=[]

## [2026-10-07T20:55:16+00:00] Step3-tdd — done
2 tests (unit=True, integration=True), 2 steps, coverage>=80%

## [2026-10-07T20:55:16+00:00] Step4-export — done
wrote /tmp/dj-out/FEATURE_SPEC.md + /tmp/dj-out/FEATURE_SPEC.html

## [2026-10-07T20:55:26+00:00] Step0-refinement — done
mock: refined ticket — clarify search scope and data source

## [2026-10-07T20:55:26+00:00] Step1-dod — done
1 contracts, 7 DoD items, 2 milestones

## [2026-10-07T20:55:26+00:00] Step2-specs — done
PRD goal: mock: deliver semantic search over markets | 3 components, 5 OWASP checks

## [2026-10-07T20:55:26+00:00] Critic-gate — approved
approved=True missing=[] issues=[]

## [2026-10-07T20:55:26+00:00] Step3-tdd — done
2 tests (unit=True, integration=True), 2 steps, coverage>=80%

## [2026-10-07T20:55:26+00:00] Step4-export — done
wrote docs/FEATURE_SPEC.md + docs/FEATURE_SPEC.html

## [2026-10-12T20:23:00+00:00] Repository-context — done
not_requested

## [2026-10-12T20:23:00+00:00] Step0-refinement — done
Implement and verify: Add a search endpoint for markets

## [2026-10-12T20:23:00+00:00] Step1-dod — done
1 contracts, 7 DoD items, 2 milestones

## [2026-10-12T20:23:00+00:00] Step2-specs — done
PRD goal: Implement: Add a search endpoint for markets | 3 components, 5 OWASP checks

## [2026-10-12T20:23:01+00:00] Critic-gate — approved
approved=True missing=[] issues=[]

## [2026-10-12T20:23:01+00:00] Step3-tdd — done
3 tests (unit=True, integration=True), 2 steps, coverage>=80%

## [2026-10-12T20:23:01+00:00] Critic-final — approved
approved=True missing=[]

## [2026-10-12T20:23:11+00:00] Step4-export — done
wrote /tmp/dev-journey-search/FEATURE_SPEC.md + /tmp/dev-journey-search/FEATURE_SPEC.html + /tmp/dev-journey-search/FEATURE_SPEC.pdf + /tmp/dev-journey-search/FEATURE_CASE_STUDY.html + /tmp/dev-journey-search/FEATURE_CASE_STUDY.pdf

## [2026-10-12T20:26:17+00:00] Repository-context — done
not_requested

## [2026-10-12T20:26:17+00:00] Step0-refinement — done
Implement and verify: Add a search endpoint for markets

## [2026-10-12T20:26:17+00:00] Step1-dod — done
1 contracts, 7 DoD items, 2 milestones

## [2026-10-12T20:26:17+00:00] Step2-specs — done
PRD goal: Implement: Add a search endpoint for markets | 3 components, 5 OWASP checks

## [2026-10-12T20:26:17+00:00] Critic-gate — approved
approved=True missing=[] issues=[]

## [2026-10-12T20:26:17+00:00] Step3-tdd — done
3 tests (unit=True, integration=True), 2 steps, coverage>=80%

## [2026-10-12T20:26:17+00:00] Critic-final — approved
approved=True missing=[]

## [2026-10-12T20:26:26+00:00] Step4-export — done
wrote /tmp/dev-journey-search-draft/FEATURE_SPEC.md + /tmp/dev-journey-search-draft/FEATURE_SPEC.html + /tmp/dev-journey-search-draft/FEATURE_SPEC.pdf + /tmp/dev-journey-search-draft/FEATURE_CASE_STUDY.html + /tmp/dev-journey-search-draft/FEATURE_CASE_STUDY.pdf

## [2026-10-14T13:59:55+00:00] Repository-context — done
not_requested

## [2026-10-14T13:59:55+00:00] Step0-refinement — done
mock: refined ticket — clarify search scope and data source

## [2026-10-14T13:59:55+00:00] Pipeline-gate — needs-input
High-severity gap: scope — mock gap: undefined search scope | Clarification required: mock: which data source?

## [2026-10-14T13:59:56+00:00] Repository-context — done
not_requested

## [2026-10-14T13:59:56+00:00] Step0-refinement — done
mock: refined ticket — clarify search scope and data source

## [2026-10-14T13:59:56+00:00] Step1-dod — done
1 contracts, 7 DoD items, 2 milestones

## [2026-10-14T13:59:57+00:00] Step2-specs — done
PRD goal: mock: deliver semantic search over markets | 3 components, 5 OWASP checks

## [2026-10-14T13:59:57+00:00] Critic-gate — needs-attention
approved=False missing=['traceability: Requirement REQ-002 has no acceptance criterion', 'traceability: Requirement REQ-001 has no acceptance criterion', 'traceability: Contract CON-001 is not linked to a requirement'] issues=['Requirement REQ-002 has no acceptance criterion', 'Requirement REQ-001 has no acceptance criterion', 'Contract CON-001 is not linked to a requirement']

## [2026-10-14T13:59:57+00:00] Step3-tdd — done
3 tests (unit=True, integration=True), 2 steps, coverage>=80%

## [2026-10-14T13:59:57+00:00] Critic-final — needs-attention
approved=False missing=['traceability: Requirement REQ-002 has no acceptance criterion', 'traceability: Requirement REQ-001 has no acceptance criterion', 'traceability: Contract CON-001 is not linked to a requirement', 'traceability: Test TEST-002 has no traceability reference', 'traceability: Test TEST-003 has no traceability reference']

## [2026-10-14T14:00:00+00:00] Step4-export — done
wrote /tmp/dev-journey-agent-matrix.IFG499/draft/FEATURE_SPEC.md + /tmp/dev-journey-agent-matrix.IFG499/draft/FEATURE_SPEC.html + /tmp/dev-journey-agent-matrix.IFG499/draft/FEATURE_CASE_STUDY.html

## [2026-10-14T14:00:01+00:00] Repository-context — done
not_requested

## [2026-10-14T14:00:01+00:00] Step0-refinement — done
Implement and verify: Add search

## [2026-10-14T14:00:02+00:00] Step1-dod — done
1 contracts, 7 DoD items, 2 milestones

## [2026-10-14T14:00:02+00:00] Step2-specs — done
PRD goal: Implement: Add search | 3 components, 5 OWASP checks

## [2026-10-14T14:00:03+00:00] Critic-gate — approved
approved=True missing=[] issues=[]

## [2026-10-14T14:00:03+00:00] Step3-tdd — done
3 tests (unit=True, integration=True), 2 steps, coverage>=80%

## [2026-10-14T14:00:04+00:00] Critic-final — approved
approved=True missing=[]

## [2026-10-14T14:00:08+00:00] Step4-export — done
wrote /tmp/dev-journey-agent-matrix.IFG499/normal/FEATURE_SPEC.md + /tmp/dev-journey-agent-matrix.IFG499/normal/FEATURE_SPEC.html + /tmp/dev-journey-agent-matrix.IFG499/normal/FEATURE_CASE_STUDY.html

## [2026-10-14T17:30:00+02:00] Portfolio quick-win — queued
The next implementation milestone is a credential-free two-scenario portfolio
demo: one approved mock run and one intentionally needs-input/draft run,
collected under separate artifact bundles and indexed by `DEMO_SUMMARY.html`.
The wrapper must make the expected provisional exit code explicit and exit
successfully only when both scenario outcomes and artifact assertions pass.

The project remains CLI/GitHub-Action-first for this milestone. MCP, Codex,
Claude, OpenCode, Gemini, hosted-service, automatic-trigger, and richer
dashboard integrations are recorded as deferred possible future features until
the quick-win demo is polished and easy to review.
