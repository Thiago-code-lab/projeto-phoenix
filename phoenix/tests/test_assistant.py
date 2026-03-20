from __future__ import annotations

from phoenix.modules.assistant.controller import AssistantController


def test_rule_based_response() -> None:
    controller = AssistantController()
    text = controller._rule_based("quero foco")  # noqa: SLF001
    assert isinstance(text, str)
    assert text


def test_parse_intent_sync_unknown() -> None:
    controller = AssistantController()
    raw = controller._parse_intent_sync("comando desconhecido")  # noqa: SLF001
    assert raw
    assert "intent" in raw
