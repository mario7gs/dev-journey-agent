from tools.repo_summarizer import summarize, to_state_dict


def test_summarize_python_and_skip():
    files = {
        "a.py": "def foo():\n    pass\n",
        "__pycache__/c.pyc": "x",
        "big.py": "x" * 10000,
    }
    ctx = summarize(files, budget_tokens=100)
    paths = [c.path for c in ctx.chunks]
    assert "a.py" in paths
    assert "__pycache__/c.pyc" in ctx.skipped
    d = to_state_dict(ctx)
    assert "chunks" in d and "total_tokens_est" in d
