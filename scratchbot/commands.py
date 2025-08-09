"""Utilities for parsing ScratchBot slash commands."""

from __future__ import annotations

import re
from typing import Optional, Tuple

COMMAND_RE = re.compile(r"^/scratchbot\s+(apply|dismiss|mode)(?:\s+(.*))?", re.IGNORECASE)


def parse_slash_command(body: str) -> Optional[Tuple[str, str]]:
    """Parse a slash command from ``body``.

    Parameters
    ----------
    body:
        Full comment text.

    Returns
    -------
    tuple | None
        ``(command, args)`` if a slash command is present, otherwise ``None``.
    """
    match = COMMAND_RE.search(body.strip())
    if not match:
        return None
    command = match.group(1).lower()
    args = (match.group(2) or "").strip()
    return command, args
