from types import SimpleNamespace

import ask


def fake_response(*blocks):
    """Build an object shaped like a real Claude response."""
    return SimpleNamespace(content=list(blocks))


def test_ask_ignores_thinking_blocks(monkeypatch):
    response = fake_response(
        SimpleNamespace(type="thinking", thinking="Let me work this out..."),
        SimpleNamespace(type="text", text="The learning rate is alpha."),
    )
    monkeypatch.setattr(ask.client.messages, "create", lambda **kwargs: response)

    assert ask.ask("some document", "some question") == "The learning rate is alpha."


def test_ask_sends_document_question_and_grounding_rules(monkeypatch):
    captured = {}

    def fake_create(**kwargs):
        captured.update(kwargs)
        return fake_response(SimpleNamespace(type="text", text="ok"))

    monkeypatch.setattr(ask.client.messages, "create", fake_create)
    ask.ask("MY NOTES", "MY QUESTION")

    content = captured["messages"][0]["content"]
    assert "MY NOTES" in content
    assert "MY QUESTION" in content
    assert "only the document" in captured["system"]