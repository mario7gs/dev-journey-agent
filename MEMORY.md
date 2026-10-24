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

## [2026-10-15T16:45:00+02:00] Portfolio quick-win — implemented
Implemented `scripts/run_portfolio_demo.sh` with two credential-free mock
scenarios: an approved health-check plan and a needs-input safety-gate plan.
The wrapper writes separate evidence bundles, cost summaries, security-audit
output, and `DEMO_SUMMARY.html`; it returns zero only after both expected
outcomes and artifact assertions pass. Added focused subprocess verification;
the full suite now passes 75 tests.

## [2026-10-15T18:55:00+02:00] Brand compliance audit — passed
Audited the generated stakeholder report, case-study presentation, and
`DEMO_SUMMARY.html` against the canonical brand guide. All now embed the
approved v19 mark and use the shared Ink/Indigo/Teal/Mist/Paper/Line tokens;
the older violet/mint case-study palette was removed. Source-level assertions,
HTML parsing, and the full 75-test release suite pass. Browser/PDF rendering
could not complete in this sandbox because the installed headless browsers
crash at process level; CI or a local desktop renderer remains the final visual
confirmation step.

## [2026-10-15T19:20:00+02:00] Approved artifact contract — locked
The stakeholder report, case-study presentation, and `DEMO_SUMMARY.html` now
share the approved v19 logo lockup, canonical palette, and sticky semantic
section navigation. This presentation baseline is frozen for the portfolio
MVP; visual changes require an explicit design decision and refreshed tests and
evidence. The provider-neutral local skill wrapper is now implemented as a
thin JSON adapter around the existing CLI. It isolates bundle state, redacts
console evidence, and preserves pipeline exit codes. MCP, provider-specific
adapters, hosted services, and automatic issue/PR integrations remain deferred.

## [2026-10-15T20:48:43+02:00] HTML navigation standardization — passed
Standardized every project documentation HTML surface with the frozen sticky
navigation contract: approved mark, `DEV JOURNEY`, exact
`AGENT · FEATURE PLANNING COPILOT` subtitle, section buttons, semantic anchors,
and print-safe behavior. The generated demo/report artifacts were audited and
already comply. Added a documentation-wide regression check; the full suite
now passes 80 tests.

## [2026-10-15T21:03:14+02:00] Delivery-hardening split — Part 1 complete

Completed the engineering release gate: reran the credential-free approved and
needs-input portfolio scenarios, refreshed their separate evidence bundles and
`DEMO_SUMMARY.html`, and verified the frozen branded HTML contract. Part 2 is
queued for the next session: final PDF visual QA, package-build verification,
publication handoff, and concise LinkedIn/GitHub portfolio support materials.
The CLI and GitHub Action remain core surfaces; MCP and provider-specific
integrations remain deferred.

## [2026-10-19T18:54:10+02:00] Delivery-hardening Part 2 — implemented with environment follow-ups

Added the self-contained six-section HTML portfolio deck and the publication
kit with LinkedIn copy, GitHub README insert, screenshot captions, walkthrough,
and claim-to-evidence map. The portfolio demo was refreshed and the release
suite now passes 81 tests. PDF visual QA and `uv build` were attempted but the
available browser binaries crash before rendering and the sandbox cannot fetch
Hatchling; keep those as explicit follow-ups in a normal developer environment.

## [2026-10-22T22:11:16+00:00] Repository-context — done
not_requested

## [2026-10-22T22:11:16+00:00] Step0-refinement — done
mock: refined ticket — clarify search scope and data source

## [2026-10-22T22:11:16+00:00] Pipeline-gate — needs-input
High-severity gap: scope — mock gap: undefined search scope | Clarification required: mock: which data source?

## [2026-10-23T00:12:42+02:00] Real validation — passed
Recorded the operator's approved read-only run against
`mario7gs/dev-journey-agent@main` for the health-check ticket: exit code 0,
GitHub status success, run ID `1282e851d5ad49649fe66182c15f9ad6`, and the
stakeholder/portfolio exports were generated. Reran the complementary
credential-free ambiguous-ticket case: status needs_input, exit code 2, with
the missing search scope/data source named explicitly. No credential value was
stored; no repository, issue, pull request, merge, or deployment mutation was
performed. Evidence is documented in `docs/MVP/REAL_TEST_CASE_REPORT.md`.

## [2026-10-23T00:16:46+02:00] Real validation runner — implemented
Added `scripts/run_real_test_case.sh` to repeat the approved repository case
and the credential-free needs-input case with separate bundles. The runner
requires a pre-exported token, never prints or persists it, unsets it before
the safety case, and validates both status payloads and key artifacts. Added a
missing-token regression test; the full suite now passes 83 tests.

## [2026-10-23T00:22:09+02:00] Real validation runner — passed
The operator executed `scripts/run_real_test_case.sh` successfully. The
approved bundle returned status approved, GitHub success, and exit code 0 with
run ID `bdaf8c0e5a5c4c18b2a07cf3d9de8d82`; the needs-input bundle returned
needs_input, GitHub failure, and exit code 2 with run ID
`f7082fe4864bb4f209a670666f81996b8`. The combined runner exited successfully.

## [2026-10-23T00:25:13+02:00] Portfolio handoff — ready
Added `docs/MVP/PORTFOLIO_HANDOFF.md` as the reviewer-first route through the
deck, credential-free demo, external validation report, engineering boundaries,
claim-to-evidence map, release gate, and deferred scope. The portfolio delivery
path is complete; PDF visual QA and `uv build` remain environment-dependent
follow-ups.

## [2026-10-23T00:37:08+02:00] Public repository and presentation polish — passed
Reframed the portfolio deck and publication kit for nontechnical and HR
readers, added an HR-friendly LinkedIn post, and made the README explain the
product in plain language. Added lightweight contribution and security policy
guidance. The full 83-test release gate remains green and the secret audit
passes.

## [2026-10-24T00:00:00+02:00] GitHub portfolio publication — release correction
The GitHub audit found no remote tag or release, so earlier historical wording
claiming that `v0.1.0` was published is superseded. The tested release matrix
is complete; creating the first tag/release is a deliberate post-merge
publishing action, not completed evidence.
