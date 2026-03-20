from __future__ import annotations

import pytest

from phoenix.modules.reviews.widgets import ReviewForm

pytestmark = [pytest.mark.ui]


def test_review_form_payload_and_validation(app) -> None:
    form = ReviewForm(["Saude", "Financas"])
    assert form.validator.is_valid() is False

    form.period_label.setText("2026-W12")
    assert form.validator.is_valid() is True

    payload = form.payload()
    assert payload["period_label"] == "2026-W12"
    assert "Saude" in payload["scores"]
    assert payload["scores"]["Saude"] >= 0
