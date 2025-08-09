"""Generate documentation plan using a language model.

The module exposes :func:`call_openai` which can either invoke a real OpenAI
model or return stubbed JSON for deterministic tests. If the environment
variable ``SCRATCHBOT_PLAN_JSON`` points to a file, its contents are returned
instead of contacting the API. Otherwise the ``openai`` package is used with
the API key in ``OPENAI_API_KEY``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable, Dict, Any


class PlanError(RuntimeError):
    """Raised when the model output cannot be parsed."""


def call_openai(prompt: str) -> str:
    """Return model output for ``prompt``.

    ``SCRATCHBOT_PLAN_JSON`` may point to a JSON file used for deterministic
    testing. When unset, the function attempts to call the real OpenAI API
    using the ``openai`` package. Set ``OPENAI_API_KEY`` and optionally
    ``OPENAI_MODEL`` to choose the model name.
    """

    stub_path = os.environ.get("SCRATCHBOT_PLAN_JSON")
    if stub_path:
        return Path(stub_path).read_text(encoding="utf-8")

    try:
        from openai import OpenAI  # type: ignore
    except Exception as exc:  # pragma: no cover - requires optional dep
        raise RuntimeError(
            "openai package not installed; set SCRATCHBOT_PLAN_JSON for tests"
        ) from exc

    client = OpenAI()
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    response = client.responses.create(model=model, input=prompt)
    return response.output_text


def generate_docs_plan(
    context: Dict[str, Any],
    call_model: Callable[[str], str] | None = None,
) -> Dict[str, Any]:
    """Call ``call_model`` with a prompt derived from ``context``.

    ``call_model`` defaults to :func:`call_openai`. The callable must accept a
    single string prompt and return the model's raw text response. The response
    is parsed as JSON with ``missing`` and ``needs_update`` lists.
    """

    if call_model is None:
        call_model = call_openai

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
