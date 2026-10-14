"""Read-only repository context assembly for Step 0."""
from __future__ import annotations

from typing import Any

from config.security_guardrails import MAX_FILE_BYTES, SKIP_DIRS, SKIP_SUFFIXES
from tools.github_client import GitHubError, RepoFile, fetch_file, fetch_tree
from tools.repo_summarizer import summarize, to_state_dict


class RepositoryContextError(RuntimeError):
    """Raised when the requested repository context cannot be assembled."""


def _skip_path(path: str) -> bool:
    parts = path.split("/")
    return any(part in SKIP_DIRS for part in parts) or path.endswith(SKIP_SUFFIXES)


def _priority(item: RepoFile) -> tuple[int, int, str]:
    """Prefer project manifests and application code over generated assets."""
    lower = item.path.lower()
    basename = lower.rsplit("/", 1)[-1]
    if basename in {
        "readme.md",
        "pyproject.toml",
        "package.json",
        "go.mod",
        "cargo.toml",
        "pom.xml",
        "build.gradle",
    }:
        rank = 0
    elif lower.startswith(("src/", "app/", "lib/", "tests/")):
        rank = 1
    else:
        rank = 2
    return rank, item.size, item.path


def build_repository_context(
    repo_ref: str,
    branch: str = "main",
    token: str = "",
    budget_tokens: int = 20_000,
    max_files: int = 80,
) -> dict[str, Any]:
    """Fetch bounded source context and turn it into Step 0 state data.

    The function is deliberately read-only. A missing repository is represented
    as ``not_requested``; a requested repository that cannot be read raises a
    typed error so the caller can apply blocking or draft policy explicitly.
    """
    if not repo_ref:
        return {
            "status": "not_requested",
            "repo_ref": "",
            "branch": branch,
            "chunks": [],
            "skipped": [],
            "total_tokens_est": 0,
        }

    try:
        tree = fetch_tree(repo_ref, branch=branch, token=token)
    except GitHubError as exc:
        raise RepositoryContextError(str(exc)) from exc

    files: dict[str, str] = {}
    skipped: list[str] = []
    for item in sorted(tree, key=_priority):
        if _skip_path(item.path) or item.size > MAX_FILE_BYTES:
            skipped.append(item.path)
            continue
        if len(files) >= max_files:
            skipped.append(item.path)
            continue
        try:
            files[item.path] = fetch_file(repo_ref, item.path, branch=branch, token=token)
        except GitHubError:
            skipped.append(item.path)

    context = to_state_dict(summarize(files, budget_tokens=budget_tokens))
    context.update(
        {
            "status": "ready",
            "repo_ref": repo_ref,
            "branch": branch,
            "files_considered": sorted(files),
            "fetch_skipped": sorted(set(skipped)),
        }
    )
    return context
