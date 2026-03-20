from __future__ import annotations

from datetime import date, datetime

import pytest

from phoenix.core.database import get_session
from phoenix.core.models import FocusSession, Goal, Habit, JournalEntry, Note, Project, Task, Transaction
from phoenix.core.repository import Repository

pytestmark = [pytest.mark.unit]


def test_goal_crud_regression() -> None:
    with get_session() as session:
        repo = Repository(session, Goal)
        created = repo.create(title="CRUD Goal")
        assert repo.get_by_id(created.id) is not None
        updated = repo.update(created, status="completed")
        assert updated.status == "completed"
        repo.delete(updated)
        assert repo.get_by_id(created.id) is None


def test_habit_crud_regression() -> None:
    with get_session() as session:
        repo = Repository(session, Habit)
        created = repo.create(name="CRUD Habit")
        assert created.id is not None
        updated = repo.update(created, active=False)
        assert updated.active is False
        repo.delete(updated)
        assert repo.get_by_id(created.id) is None


def test_transaction_crud_regression() -> None:
    with get_session() as session:
        repo = Repository(session, Transaction)
        created = repo.create(title="CRUD Tx", amount=10.0, type="income", date=date.today())
        assert created.id is not None
        updated = repo.update(created, amount=12.0)
        assert updated.amount == 12.0
        repo.delete(updated)
        assert repo.get_by_id(created.id) is None


def test_project_task_crud_regression() -> None:
    with get_session() as session:
        project_repo = Repository(session, Project)
        task_repo = Repository(session, Task)
        project = project_repo.create(name="CRUD Project")
        task = task_repo.create(project_id=project.id, title="CRUD Task")
        assert task.project_id == project.id
        task_repo.delete(task)
        project_repo.delete(project)
        assert project_repo.get_by_id(project.id) is None


def test_focus_note_journal_crud_regression() -> None:
    with get_session() as session:
        focus_repo = Repository(session, FocusSession)
        note_repo = Repository(session, Note)
        journal_repo = Repository(session, JournalEntry)

        focus = focus_repo.create(date=date.today(), start_time=datetime.now(), duration_min=25, completed=True)
        note = note_repo.create(title="CRUD Note", content="texto")
        entry = journal_repo.create(date=date.today(), title="CRUD Journal", content="ok")

        assert focus.id and note.id and entry.id

        focus_repo.delete(focus)
        note_repo.delete(note)
        journal_repo.delete(entry)
        assert focus_repo.get_by_id(focus.id) is None
