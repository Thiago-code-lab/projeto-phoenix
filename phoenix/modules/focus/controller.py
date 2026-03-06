from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import select

from phoenix.core.database import get_session
from phoenix.core.models import FocusSession
from phoenix.core.repository import Repository


class FocusController:
    def save_session(self, data: dict) -> FocusSession:
        start_time = data.get("start_time") or datetime.now()
        with get_session() as session:
            return Repository(session, FocusSession).create(
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
