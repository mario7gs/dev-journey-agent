"""PyGithub client: read-only repo access (tree, file, diff).

All functions are thin wrappers with typed errors so agents and
tests can mock at the Github class boundary (no network in tests).
"""
from __future__ import annotations

from dataclasses import dataclass


class GitHubError(RuntimeError):
    pass


@dataclass(frozen=True)
class RepoFile:
    path: str
    size: int
    sha: str


def _client(token: str = ""):
    from github import Github

    if token:
        return Github(token)
    return Github()


def fetch_tree(repo_ref: str, branch: str = "main", token: str = "") -> list[RepoFile]:
    """List files on branch. Raises GitHubError on auth/network failure."""
    try:
        gh = _client(token)
        repo = gh.get_repo(repo_ref)
        contents = repo.get_contents("", ref=branch)
        # get_contents may return a single object for a file; normalize to list
        items = contents if isinstance(contents, list) else [contents]
        out: list[RepoFile] = []
        stack = list(items)
        while stack:
            item = stack.pop()
            if item.type == "dir":
                stack.extend(repo.get_contents(item.path, ref=branch))
            else:
                out.append(RepoFile(path=item.path, size=item.size or 0, sha=item.sha or ""))
        return out
    except Exception as exc:
        raise GitHubError(f"fetch_tree failed for {repo_ref}@{branch}: {exc}") from exc


def fetch_file(repo_ref: str, path: str, branch: str = "main", token: str = "") -> str:
    """Return decoded file content. Raises GitHubError on failure."""
    try:
        gh = _client(token)
        repo = gh.get_repo(repo_ref)
        content = repo.get_contents(path, ref=branch)
        if isinstance(content, list):
            raise GitHubError(f"Path is a directory: {path}")
        return content.decoded_content.decode("utf-8", errors="replace")
    except GitHubError:
        raise
    except Exception as exc:
        raise GitHubError(f"fetch_file failed for {path}: {exc}") from exc
