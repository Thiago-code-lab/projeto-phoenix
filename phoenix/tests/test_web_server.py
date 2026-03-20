from __future__ import annotations

from phoenix.web.server import build_payload, detect_backend


def test_detect_backend_is_known() -> None:
    assert detect_backend() in {"fastapi", "stdlib"}


def test_build_payload_shape() -> None:
    payload = build_payload()
    assert payload.get("status") == "ok"
    assert payload.get("backend") in {"fastapi", "stdlib"}
    summary = payload.get("summary")
    assert isinstance(summary, dict)
    assert "goals_total" in summary
    assert "habits_active" in summary
    assert "transactions_month" in summary
    assert "focus_sessions_recent" in summary
