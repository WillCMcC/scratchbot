"""Generate documentation plan using a language model."""

from __future__ import annotations

import json
from typing import Callable, Dict, Any


class PlanError(RuntimeError):
    """Raised when the model output cannot be parsed."""


def generate_docs_plan(context: Dict[str, Any], call_model: Callable[[str], str]) -> Dict[str, Any]:
    """Call ``call_model`` with a prompt derived from ``context``.

    The callable must accept a single string prompt and return the model's
    raw text response. The response is parsed as JSON with ``missing`` and
    ``needs_update`` lists.
    """
    prompt = (
        "You are ScratchBot. Given the diff, file tree and symbol summaries, "
        "produce a JSON object with keys 'missing' and 'needs_update'."\
    )
    prompt += "\nDiff:\n" + context["diff"]
    prompt += "\nFile Tree:\n" + context["file_tree"]
    prompt += "\nSymbols:\n" + ", ".join(
        f"{s.path}: {', '.join(s.symbols)}" for s in context.get("summaries", [])
    )

    raw = call_model(prompt)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise PlanError("model did not return valid JSON") from exc
    if not {"missing", "needs_update"} <= data.keys():
        raise PlanError("JSON must contain missing and needs_update")
    if not isinstance(data["missing"], list) or not isinstance(data["needs_update"], list):
        raise PlanError("missing and needs_update must be lists")
    return data
