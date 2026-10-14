"""Mocked PyGithub boundary — no network."""
from tools.github_client import GitHubError, fetch_file, fetch_tree


class _FakeContent:
    def __init__(self, path, type="file", size=10, sha="abc"):
        self.path = path
        self.type = type
        self.size = size
        self.sha = sha
        self.decoded_content = b"hello"


class _FakeRepo:
    def get_contents(self, path, ref="main"):
        if path == "":
            return [_FakeContent("a.py")]
        return _FakeContent(path)


class _FakeGithub:
    def __init__(self, *a, **k):
        pass

    def get_repo(self, ref):
        if ref == "bad/repo":
            raise RuntimeError("404")
        return _FakeRepo()


def test_fetch_tree_ok(monkeypatch):
    import tools.github_client as gc

    monkeypatch.setattr(gc, "_client", lambda token="": _FakeGithub())
    out = fetch_tree("owner/repo")
    assert out and out[0].path == "a.py"


def test_fetch_tree_error(monkeypatch):
    import tools.github_client as gc

    monkeypatch.setattr(gc, "_client", lambda token="": _FakeGithub())
    try:
        fetch_tree("bad/repo")
    except GitHubError:
        return
    raise AssertionError("expected GitHubError")


def test_fetch_file_ok(monkeypatch):
    import tools.github_client as gc

    monkeypatch.setattr(gc, "_client", lambda token="": _FakeGithub())
    assert fetch_file("owner/repo", "a.py") == "hello"
