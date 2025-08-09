"""Assemble context for documentation planning.

This module provides utilities to collect a git diff, file tree, and
symbol summaries for a repository.  The result is bounded by a token
limit (approximate using whitespace separated words).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import ast
import subprocess
from typing import Dict, List

TOKEN_LIMIT = 150_000


@dataclass
class FileSummary:
    path: str
    symbols: List[str]
    loc: int


def _token_count(text: str) -> int:
    return len(text.split())


def _python_symbols(path: Path) -> List[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    symbols: List[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                symbols.append(node.name)
    return symbols


def build_file_summaries(repo: Path) -> List[FileSummary]:
    summaries: List[FileSummary] = []
    for file in repo.rglob("*.py"):
        rel = file.relative_to(repo).as_posix()
        text = file.read_text(encoding="utf-8")
        symbols = _python_symbols(file)
        loc = text.count("\n") + 1
        summaries.append(FileSummary(path=rel, symbols=symbols, loc=loc))
    return summaries


def assemble_context(repo: str | Path, base_ref: str = "origin/main") -> Dict[str, object]:
    """Return diff, tree, symbol summaries and token count for ``repo``.

    Raises ``ValueError`` if the approximate token count exceeds
    ``TOKEN_LIMIT``.
    """
    repo = Path(repo)
    diff = subprocess.run(
        ["git", "-C", str(repo), "diff", f"{base_ref}...HEAD"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout

    tree_lines = [p.as_posix() for p in sorted(repo.rglob("*")) if p.is_file()]
    tree = "\n".join(tree_lines)

    summaries = build_file_summaries(repo)
    summaries_text = "\n".join(
        f"{s.path}: {', '.join(s.symbols)}" for s in summaries
    )

    total_tokens = _token_count(diff) + _token_count(tree) + _token_count(summaries_text)
    if total_tokens > TOKEN_LIMIT:
        raise ValueError("context exceeds token limit")

    return {
        "diff": diff,
        "file_tree": tree,
        "summaries": summaries,
        "tokens": total_tokens,
    }
