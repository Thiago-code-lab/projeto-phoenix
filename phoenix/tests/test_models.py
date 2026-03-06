from phoenix.core.models import Goal, Habit, Note


def test_goal_model_defaults() -> None:
    goal = Goal(title="Meta principal")
    assert goal.status == "active"
    assert goal.current_value == 0


def test_habit_model_defaults() -> None:
    habit = Habit(name="Leitura")
    assert habit.frequency == "daily"
    assert habit.active is True


def test_note_defaults() -> None:
    note = Note(title="Base")
    assert note.pinned is False
