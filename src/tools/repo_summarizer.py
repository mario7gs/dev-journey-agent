"""Chunking + AST summarization for large repos.

Pure functions (no network, no LLM) — fully unit-testable.
"""
from __future__ import annotations

import ast
from dataclasses import dataclass

from config.security_guardrails import SKIP_DIRS, SKIP_SUFFIXES


@dataclass(frozen=True)
class CodeChunk:
    path: str
    summary: str
    tokens_est: int


@dataclass(frozen=True)
class CodeContext:
    chunks: tuple[CodeChunk, ...] = ()
    skipped: tuple[str, ...] = ()
    total_tokens_est: int = 0


def _should_skip(path: str) -> bool:
    parts = path.split("/")
    if any(p in SKIP_DIRS for p in parts):
        return True
    return path.endswith(SKIP_SUFFIXES)


def _summarize_python(source: str) -> str:
    """AST summary: top-level defs/classes. Falls back to line count."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        lines = source.count("\n") + 1
        return f"unparsable python, {lines} lines"
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.append(f"{type(node).__name__}:{node.name}")
    if not names:
        return f"python module, {len(tree.body)} top-level statements"
    return "defines " + ", ".join(names[:20])


def summarize(
    files: dict[str, str],
    budget_tokens: int = 20_000,
) -> CodeContext:
    """Build budgeted CodeContext. Immutable — returns new objects."""
    chunks: list[CodeChunk] = []
    skipped: list[str] = []
    total = 0
    for path in sorted(files):
        if _should_skip(path):
            skipped.append(path)
            continue
        source = files[path]
        summary = _summarize_python(source) if path.endswith(".py") else f"text, {len(source)} chars"
        tokens_est = max(1, len(source) // 4)
        if total + tokens_est > budget_tokens:
            skipped.append(path)
            continue
        total += tokens_est
        chunks.append(CodeChunk(path=path, summary=summary, tokens_est=tokens_est))
    return CodeContext(chunks=tuple(chunks), skipped=tuple(skipped), total_tokens_est=total)


def to_state_dict(ctx: CodeContext) -> dict:
    return {
        "chunks": [{"path": c.path, "summary": c.summary} for c in ctx.chunks],
        "skipped": list(ctx.skipped),
        "total_tokens_est": ctx.total_tokens_est,
    }
