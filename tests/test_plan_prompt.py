from scratchbot.plan_prompt import call_openai, generate_docs_plan


def test_call_openai_stub(tmp_path, monkeypatch):
    stub = tmp_path / "stub.json"
    stub.write_text('{"missing": [], "needs_update": []}')
    monkeypatch.setenv("SCRATCHBOT_PLAN_JSON", str(stub))
    assert call_openai("prompt") == stub.read_text()


def test_generate_docs_plan_defaults_to_call_openai(tmp_path, monkeypatch):
    stub = tmp_path / "stub.json"
    stub.write_text('{"missing": ["a"], "needs_update": []}')
    monkeypatch.setenv("SCRATCHBOT_PLAN_JSON", str(stub))
    context = {"diff": "", "file_tree": "", "summaries": []}
    assert generate_docs_plan(context) == {"missing": ["a"], "needs_update": []}
