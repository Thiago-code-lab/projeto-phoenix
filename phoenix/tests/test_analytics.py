from __future__ import annotations

from datetime import date

from phoenix.core.database import SessionLocal, init_database
from phoenix.modules.analytics.controller import AnalyticsController


def test_life_score_shape() -> None:
    init_database()
    controller = AnalyticsController()
    session = SessionLocal()
    try:
        scores = controller.get_life_score(session)
        assert set(scores.keys()) == {"habits", "finances", "focus", "goals", "health", "diary"}
    finally:
        session.close()


def test_report_data_period() -> None:
    init_database()
    controller = AnalyticsController()
    session = SessionLocal()
    try:
        payload = controller.get_life_report_data(session, date.today().month, date.today().year)
        assert "period" in payload
    finally:
        session.close()
