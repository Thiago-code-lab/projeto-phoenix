from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import select

from phoenix.core.database import db_operation_class, get_session
from phoenix.core.models import FocusSession, Project, Task
from phoenix.core.repository import Repository


@db_operation_class
class FocusController:
    def save_session(self, data: dict) -> FocusSession:
        start_time = data.get("start_time") or datetime.now()
        with get_session() as session:
            return Repository(session, FocusSession).create(
                task_id=int(data.get("task_id")) if data.get("task_id") else None,
                date=data.get("date") or date.today(),
                start_time=start_time,
                duration_min=int(data.get("duration_min", 0)),
                task_name=str(data.get("task_name", "")).strip() or None,
                completed=bool(data.get("completed", True)),
            )

    def get_sessions(self, start: date, end: date) -> list[FocusSession]:
        with get_session() as session:
            query = select(FocusSession).where(FocusSession.date >= start, FocusSession.date <= end).order_by(FocusSession.start_time.desc())
            return list(session.scalars(query).all())

    def get_weekly_stats(self) -> dict:
        today = date.today()
        start = today - timedelta(days=today.weekday())
        sessions = self.get_sessions(start, today)
        sessions_this_week = len(sessions)
        total_minutes = sum(item.duration_min for item in sessions)
        avg_session = round(total_minutes / sessions_this_week, 2) if sessions_this_week else 0

        sessions_per_day: dict[str, int] = {}
        for item in sessions:
            key = item.date.strftime("%a")
            sessions_per_day[key] = sessions_per_day.get(key, 0) + 1
        best_day = max(sessions_per_day, key=sessions_per_day.get) if sessions_per_day else "-"

        return {
            "sessions_this_week": sessions_this_week,
            "total_minutes_this_week": total_minutes,
            "avg_session_minutes": avg_session,
            "best_day": best_day,
            "sessions_per_day": sessions_per_day,
        }

    def get_today_total(self) -> int:
        sessions = self.get_sessions(date.today(), date.today())
        return sum(item.duration_min for item in sessions)

    def list_active_tasks(self) -> list[Task]:
        """Lista tarefas abertas para vinculo de sessao de foco."""

        with get_session() as session:
            return list(session.scalars(select(Task).where(Task.status != "done").order_by(Task.updated_at.desc())).all())

    def get_available_tasks(self) -> list[Task]:
        """Alias semântico para tarefas disponíveis no vínculo de foco."""

        return self.list_active_tasks()

    def weekly_report(self) -> dict[str, object]:
        """Retorna horas totais da semana e distribuicao por projeto."""

        today = date.today()
        start = today - timedelta(days=today.weekday())
        with get_session() as session:
            sessions = list(session.scalars(select(FocusSession).where(FocusSession.date >= start, FocusSession.date <= today)).all())
            projects = {item.id: item.name for item in session.scalars(select(Project)).all()}
            tasks = {item.id: item.project_id for item in session.scalars(select(Task)).all()}

        total_minutes = sum(item.duration_min for item in sessions)
        by_project: dict[str, float] = {}
        for session_item in sessions:
            project_name = "Sem projeto"
            if session_item.task_id and session_item.task_id in tasks:
                project_id = tasks.get(session_item.task_id)
                project_name = projects.get(project_id, "Sem projeto")
            by_project[project_name] = by_project.get(project_name, 0) + (session_item.duration_min / 60.0)
        return {
            "total_hours": round(total_minutes / 60.0, 2),
            "by_project": {key: round(value, 2) for key, value in by_project.items()},
        }
