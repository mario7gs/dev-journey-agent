# Dev Journey Agent — portfolio publication kit

This kit packages the final delivery-hardening story for a portfolio review.
It keeps the claim narrow: a CLI-first planning copilot with explicit safety
gates and inspectable evidence.

## One-line description

Dev Journey Agent turns a vague development ticket into a reviewable feature
plan with requirements, tests, approval gates, resumable checkpoints, and
redacted evidence.

## LinkedIn post — publish-ready

Most delivery problems do not start in code.

They start earlier, when a request sounds clear but the team has not yet made
the decisions that shape the solution.

I built Dev Journey Agent to make that gap explicit.

It takes an early development request and turns it into a reviewable planning
package: repository context, clarified requirements, definition of done,
test-oriented cases, a critic gate, checkpoints, and evidence. The purpose is
not to replace the people making the decision. It is to give them a clearer
starting point before source-code changes begin.

The important rule is that it does not force an answer. When the evidence
supports a plan, it produces an approved result. When a material gap remains,
it stops and names the question that needs human input.

I validated both outcomes: a read-only repository case produced an approved
health-check plan, while an intentionally ambiguous request returned
`needs_input` instead of presenting an unreliable plan.

The scope is deliberately small and inspectable: a CLI, a manual GitHub
Action, and a provider-neutral local wrapper. It does not change source code,
create pull requests, or deploy anything automatically.

The attached carousel explains the problem, workflow, decision gate, outputs,
and evidence. The public repository and validation material are here:
https://github.com/mario7gs/dev-journey-agent

## LinkedIn document carousel

Upload [`DEV_JOURNEY_AGENT_LINKEDIN_CAROUSEL.pdf`](../artifacts/linkedin/DEV_JOURNEY_AGENT_LINKEDIN_CAROUSEL.pdf)
as a LinkedIn document with the post above. It is an eight-page square carousel
designed to be readable on mobile and desktop.

Suggested document title: **Dev Journey Agent: from request to reviewable
plan**

The page sequence is deliberate:

1. A feature request is not an implementation plan.
2. The interpretation gap before code.
3. The proposed planning method.
4. The six-stage workflow.
5. The approval or needs-input decision gate.
6. The artifacts a reviewer can inspect.
7. The two validation outcomes.
8. The implemented scope and deliberate boundaries.

The editable source is also retained as
[`DEV_JOURNEY_AGENT_LINKEDIN_CAROUSEL.pptx`](../artifacts/linkedin/DEV_JOURNEY_AGENT_LINKEDIN_CAROUSEL.pptx).

## First comment (optional)

The source, two-scenario demo, and real test-case report are public in the
repository: https://github.com/mario7gs/dev-journey-agent

## LinkedIn post — technical alternative

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
5. `artifacts/linkedin/DEV_JOURNEY_AGENT_LINKEDIN_CAROUSEL.pdf`. Caption:
   “A concise explanation of the request-to-plan gap, the decision gate, and
   the validation evidence.”

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
PLANNING COPILOT`. Keep screenshots and the carousel focused on the evidence
and the safety behavior. Avoid presenting the project as a hosted autonomous
coding agent or claiming provider integrations that are not implemented.
