from __future__ import annotations

import ast
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


def _parse_value(value: str):
    value = value.strip()
    if value.startswith("[") or value.startswith("{"):
        return ast.literal_eval(value)
    try:
        return int(value)
    except ValueError:
        return value


def _load_simple_yaml(text: str) -> Dict[str, object]:
    root: Dict[str, object] = {}
    stack = [root]
    indents = [0]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        while indent < indents[-1]:
            stack.pop()
            indents.pop()
        key, _, value = raw.lstrip().partition(":")
        if value.strip() == "":
            new_dict: Dict[str, object] = {}
            stack[-1][key.strip()] = new_dict
            stack.append(new_dict)
            indents.append(indent + 2)
        else:
            stack[-1][key.strip()] = _parse_value(value)
    return root


@dataclass
class ScratchbotConfig:
    """Configuration loaded from ``.scratchbot.yml``.

    Attributes
    ----------
    commit_mode:
        ``"per_file"`` to commit each file individually or ``"batch"`` for a
        single commit.
    docs_dir:
        Directory where documentation files are stored.
    include / exclude:
        Optional lists of glob patterns controlling which paths are analysed.
    thresholds:
        Arbitrary integer thresholds such as line counts.
    """

    commit_mode: str = "per_file"
    docs_dir: str = "docs"
    include: List[str] = field(default_factory=list)
    exclude: List[str] = field(default_factory=list)
    thresholds: Dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: str | Path = ".scratchbot.yml") -> "ScratchbotConfig":
        """Load configuration from ``path``.

        Missing files yield default values.
        """
        cfg_path = Path(path)
        if not cfg_path.exists():
            return cls()

        data = _load_simple_yaml(cfg_path.read_text(encoding="utf-8"))
        return cls(
            commit_mode=data.get("commit_mode", "per_file"),
            docs_dir=data.get("docs_dir", "docs"),
            include=data.get("include", []) or [],
            exclude=data.get("exclude", []) or [],
            thresholds=data.get("thresholds", {}) or {},
        )
