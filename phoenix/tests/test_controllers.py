import pytest

from phoenix.modules.dashboard.controller import DashboardController

pytestmark = [pytest.mark.unit]


def test_dashboard_summary_keys() -> None:
    summary = DashboardController().summary()
    assert {"goals", "habits", "transactions", "books", "projects", "tasks"}.issubset(summary.keys())
