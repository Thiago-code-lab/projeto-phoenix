from phoenix.modules.dashboard.controller import DashboardController


def test_dashboard_summary_keys() -> None:
    summary = DashboardController().summary()
    assert {"goals", "habits", "transactions", "books", "projects", "tasks"}.issubset(summary.keys())
