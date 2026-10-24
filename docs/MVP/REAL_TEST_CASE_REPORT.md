# Dev Journey Agent — Real Test Case Report

**Validation date:** 2026-10-23  
**Scope:** end-to-end CLI validation of the approved and safety-gated outcomes

This report records the first portfolio-relevant validation against the private
GitHub repository `mario7gs/dev-journey-agent`. It is intentionally sanitized:
no token, credential value, or machine secret is stored here.

## Executive result

The two expected outcomes were demonstrated:

| Scenario | Repository access | Expected result | Observed result | Exit code |
| --- | --- | --- | --- | ---: |
| Approved health-check plan | Read-only context from `mario7gs/dev-journey-agent@main` | Approved plan and exports | `approved`, GitHub status `success` | `0` |
| Ambiguous improvement request | Credential-free deterministic fixture | Stop and ask for clarification | `needs_input`; missing search scope/data source reported | `2` |

The approved run was executed by the operator in a local terminal and supplied
as the validation log. The complementary safety case was rerun locally with
the deterministic mock path during this session. Neither scenario writes
source code, issues, pull requests, or deployments.

## Scenario A — approved real-repository run

- Ticket: `Add a health-check endpoint`
- Repository: `mario7gs/dev-journey-agent`
- Branch: `main`
- Mode: `blocking`
- Model path: deterministic mock LLM (`USE_MOCK_LLM=true`)
- Result: approved
- GitHub status: success
- Exit code: `0`
- Run ID: `1282e851d5ad49649fe66182c15f9ad6`
- Usage: `0.0` USD and `0` provider tokens because the mock path was used
- Security audit: passed; no recognizable live credentials found

The operator log reported the following generated artifact set:

- `FEATURE_SPEC.md` and `FEATURE_SPEC.html`
- `FEATURE_SPEC.pdf`
- `FEATURE_CASE_STUDY.html` and `FEATURE_CASE_STUDY.pdf`
- eight stage checkpoints, `MEMORY.md`, telemetry JSONL, and a cost summary

The original local evidence bundle was under the operator's temporary run
directory (`/tmp/tmp.Xqkx09sMg5`). Temporary paths are recorded for provenance
only and are not required for repository operation.

## Scenario B — needs-input safety gate

This session ran the deterministic fixture with the intentionally ambiguous
ticket `Improve the application` in blocking mode. It stopped before approval
with:

- status: `needs_input`
- exit code: `2`
- blocking reasons: undefined search scope and a request to identify the data
  source
- GitHub status: `failure` (the expected status for an unresolved blocking
  plan)
- run ID: `0689e2d2972f466ba7aa48139212c748`

Evidence from this verification is available in the temporary bundle:

- `/tmp/dev-journey-needs-input-test/run-status.json`
- `/tmp/dev-journey-needs-input-test/FEATURE_SPEC.md`
- `/tmp/dev-journey-needs-input-test/FEATURE_SPEC.html`

This is the important negative-path proof: the agent does not manufacture an
approved plan when a high-severity requirement gap remains unresolved.

## Reproduction of the complete validation

Once a GitHub token has been exported in the local process environment, the
repeatable runner executes both cases and retains separate evidence bundles:

```bash
export GITHUB_TOKEN
bash scripts/run_real_test_case.sh /tmp/dev-journey-real-test
```

The optional second and third arguments override the repository and branch:

```bash
bash scripts/run_real_test_case.sh /tmp/dev-journey-real-test owner/name main
```

The runner never prompts for, prints, or writes the token. It uses the token
only for read-only repository context in the approved case, then removes it
from the environment for the credential-free safety case.

### Latest runner execution — passed

The repeatable runner was executed successfully after this report was added.
Its machine-readable results were:

| Bundle | Status | GitHub signal | Exit code | Run ID |
| --- | --- | --- | ---: | --- |
| `/tmp/dev-journey-real-test/approved` | `approved` | `success` | `0` | `bdaf8c0e5a5c4c18b2a07cf3d9de8d82` |
| `/tmp/dev-journey-real-test/needs-input` | `needs_input` | `failure` | `2` | `f7082fe4864bb4f209a670666f81996b8` |

The wrapper therefore passed its own combined validation, preserving the
expected distinction between an approved plan and a safely blocked plan.

## Reproduction of the safe gate

The needs-input case requires no credentials or network access:

```bash
UV_CACHE_DIR=/tmp/dev-journey-agent-uv-cache \
USE_MOCK_LLM=true \
uv run dev-journey \
  --ticket "Improve the application" \
  --mode blocking \
  --demo \
  --out-dir /tmp/dev-journey-needs-input-test \
  --status-file /tmp/dev-journey-needs-input-test/run-status.json
```

For a real repository run, provide the GitHub credential only through the
local process environment. Never paste it into a command, commit it, or place
it in an artifact bundle. A fine-grained read-only token scoped to the target
repository is the preferred future test setup.

## Acceptance checklist

- [x] A real private-repository context was fetched successfully.
- [x] The approved blocking path returned exit code `0`.
- [x] Stakeholder and portfolio exports were generated.
- [x] The ambiguous path returned exit code `2` and `needs_input`.
- [x] The blocking reasons were specific enough to guide clarification.
- [x] The mock path incurred no provider cost.
- [x] Security evidence reported no recognizable live credentials.
- [x] No source, issue, pull request, merge, or deployment mutation occurred.
- [x] The evidence is recorded without storing a credential value.

## Position in the portfolio path

This closes the first meaningful external validation loop for the CLI-first
portfolio story: a real repository can produce a reviewable plan, while an
underspecified request is safely held for clarification. The CLI and GitHub
Action remain the core supported surfaces. MCP, hosted services,
provider-specific chat adapters, and automatic issue/PR integrations remain
deliberately deferred.
