from __future__ import annotations

from datetime import date

import pytest

from phoenix.modules.goals.controller import GoalsController

pytestmark = [pytest.mark.integration]


def test_goal_milestone_complete_flow() -> None:
    controller = GoalsController()

    goal = controller.create(
        {
            "title": "Meta integracao",
            "category": "estudos",
            "target_value": 10,
            "current_value": 0,
            "target_date": date.today().isoformat(),
        }
    )
    milestone = controller.add_milestone(
        goal.id,
        {
            "title": "Marco 1",
            "due_date": date.today().isoformat(),
        },
    )

    toggled = controller.toggle_milestone(milestone.id)
    refreshed_goal = controller.get_by_id(goal.id)

    assert toggled.completed is True
    assert refreshed_goal is not None
    assert any(item.id == milestone.id and item.completed for item in refreshed_goal.milestones)
