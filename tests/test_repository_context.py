from tools.github_client import RepoFile
from tools.repository_context import build_repository_context


def test_repository_context_fetches_bounded_source(monkeypatch):
    tree = [
        RepoFile("README.md", 20, "readme"),
        RepoFile("src/app.py", 20, "app"),
        RepoFile("node_modules/x.js", 20, "skip"),
    ]
    monkeypatch.setattr("tools.repository_context.fetch_tree", lambda *args, **kwargs: tree)
    monkeypatch.setattr(
        "tools.repository_context.fetch_file",
        lambda _repo, path, **kwargs: "def run():\n    pass\n" if path.endswith(".py") else "# project",
    )

    context = build_repository_context("owner/repo", branch="main", max_files=10)

    assert context["status"] == "ready"
    assert context["repo_ref"] == "owner/repo"
    assert "src/app.py" in context["files_considered"]
    assert "node_modules/x.js" in context["fetch_skipped"]


def test_repository_context_without_repo_is_explicit():
    context = build_repository_context("")
    assert context["status"] == "not_requested"
    assert context["chunks"] == []
