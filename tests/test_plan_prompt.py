from types import SimpleNamespace
import sys

from scratchbot.plan_prompt import call_openai, generate_docs_plan


def test_call_openai_stub(tmp_path, monkeypatch):
    stub = tmp_path / "stub.json"
    stub.write_text('{"missing": [], "needs_update": []}')
    monkeypatch.setenv("SCRATCHBOT_PLAN_JSON", str(stub))
    assert call_openai("prompt") == stub.read_text()


def test_call_openai_defaults_to_gpt5(monkeypatch):
    capture = {}

    class DummyResponses:
        def create(self, model, input):
            capture["model"] = model
            capture["input"] = input
            return SimpleNamespace(output_text="ok")

    class DummyClient:
        def __init__(self):
            self.responses = DummyResponses()

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(OpenAI=DummyClient))
    monkeypatch.delenv("SCRATCHBOT_PLAN_JSON", raising=False)
    monkeypatch.delenv("OPENAI_MODEL", raising=False)
    assert call_openai("hi") == "ok"
    assert capture["model"] == "gpt-5"


def test_generate_docs_plan_defaults_to_call_openai(tmp_path, monkeypatch):
    stub = tmp_path / "stub.json"
    stub.write_text('{"missing": ["a"], "needs_update": []}')
    monkeypatch.setenv("SCRATCHBOT_PLAN_JSON", str(stub))
    context = {"diff": "", "file_tree": "", "summaries": []}
    assert generate_docs_plan(context) == {"missing": ["a"], "needs_update": []}
