# Dev Journey Agent — portfolio publication kit

This kit packages the final delivery-hardening story for a portfolio review.
It keeps the claim narrow: a CLI-first planning copilot with explicit safety
gates and inspectable evidence.

## One-line description

Dev Journey Agent turns a vague development ticket into a reviewable feature
plan with requirements, tests, approval gates, resumable checkpoints, and
redacted evidence.

## LinkedIn post — HR-friendly version

I built Dev Journey Agent to solve a simple problem in software work:
important decisions often remain hidden between a short request and the start
of implementation.

Someone can write “add a health check” in a few words. A team still needs to
agree on what the feature should do, how success will be measured, and which
questions must be answered before work begins.

Dev Journey Agent turns that request into a clear, reviewable plan. It can:

- explain the work in plain language;
- make success criteria and risks visible;
- connect the plan to tests and evidence; and
- stop and ask for clarification when the request is too vague.

I tested it with two cases. A clear request produced an approved plan. An
ambiguous request stopped safely and asked for the missing information. The
project also keeps a recoverable record of each run and avoids storing
credentials in its artifacts.

The result is intentionally small: a command-line tool, a manual GitHub
workflow, and a provider-neutral local wrapper. The goal is not to claim a
fully autonomous software engineer. The goal is to show how AI can make the
start of technical work clearer, safer, and easier to review.

Demo and evidence: `artifacts/demo/DEMO_SUMMARY.html`

## Technical LinkedIn draft

I built Dev Journey Agent, a small CLI-first planning copilot for the gap
between a vague ticket and a safe implementation plan.

The project focuses on a practical question: what should a team be able to
review before code changes begin?

The workflow produces explicit requirements, definition of done, TDD-oriented
cases, critic gates, checkpoints, telemetry, cost evidence, and branded HTML
reports. A credential-free demo makes the behavior easy to inspect:

- an approved health-check request exits with `0`;
- an ambiguous request stops with `needs_input` and exits with `2`;
- both outcomes preserve their evidence bundles; and
- the source passes an 83-test release gate plus secret, type, and HTML checks.

The supported product surfaces stay deliberately small: the `dev-journey` CLI,
a manual GitHub Action, and a provider-neutral local JSON wrapper. MCP,
provider-specific adapters, hosted execution, and automatic issue/PR
integrations remain deferred.

Demo and evidence: `artifacts/demo/DEMO_SUMMARY.html`

## GitHub README insert

```md
### See the project in one minute

Run `bash scripts/run_portfolio_demo.sh` to see two honest outcomes from the
same planning pipeline: an approved plan and a needs-input safety gate. The
generated `artifacts/demo/DEMO_SUMMARY.html` links to the plans, checkpoints,
telemetry, cost reports, and security audit.

The project is CLI-first and credential-free for demos. The manual GitHub
Action and provider-neutral local wrapper extend the same contract without
introducing provider-specific integrations.
```

## Suggested screenshots

1. `artifacts/demo/DEMO_SUMMARY.html` at the overview section. Caption:
   “One command, two visible outcomes, with every evidence bundle linked.”
2. The approved scenario card. Caption:
   “The normal path produces a reviewable plan and an approved status.”
3. The needs-input scenario card. Caption:
   “The safety gate stops at ambiguity instead of inventing requirements.”
4. `artifacts/portfolio/DEV_JOURNEY_PORTFOLIO_DECK.html`. Caption:
   “A compact case study of the product boundary, proof, and trust layer.”

## Five-minute walkthrough

1. Open `DEMO_SUMMARY.html` and show the two different statuses.
2. Open the approved `FEATURE_SPEC.html` and point to the sticky navigation.
3. Open the needs-input `FEATURE_SPEC.html` and show the clarification state.
4. Open `run-status.json`, `cost-summary.json`, and `security-audit.txt` to
   connect the visible story to machine-readable evidence.
5. Close with the scope boundary: CLI and GitHub Action are core; integrations
   are intentionally deferred.

## Claim-to-evidence map

| Claim | Evidence |
|---|---|
| Approved path returns success | `artifacts/demo/approved/run-status.json` |
| Ambiguity stops safely | `artifacts/demo/needs-input/run-status.json` |
| Evidence is resumable | Scenario `checkpoints/` directories |
| Usage is bounded | Both `cost-summary.json` files |
| Secrets are not exposed | `artifacts/demo/security-audit.txt` |
| Brand contract is stable | `docs/BRAND_GUIDELINES.html` and HTML brand tests |
| Core surfaces stay small | `README.md`, `docs/OPERATIONS.md` |

## Publication notes

Use the supplied v19 logo and the exact lockup `DEV JOURNEY` / `AGENT · FEATURE
PLANNING COPILOT`. Keep screenshots focused on the evidence and the safety
behavior. Avoid presenting the project as a hosted autonomous coding agent or
claiming provider integrations that are not implemented.
