from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select

from phoenix.core.database import get_session
from phoenix.core.models import Habit, HabitLog
from phoenix.core.repository import Repository


class HabitsController:
    def get_all(self, active_only: bool = True) -> list[Habit]:
        with get_session() as session:
            query = select(Habit).order_by(Habit.created_at.desc())
            if active_only:
                query = query.where(Habit.active.is_(True))
            return list(session.scalars(query).all())

    def create(self, data: dict) -> Habit:
        name = str(data.get("name", "")).strip()
        if not name:
            raise ValueError("Nome do habito e obrigatorio.")
        with get_session() as session:
            return Repository(session, Habit).create(
                name=name,
                description=str(data.get("description", "")).strip() or None,
                frequency=str(data.get("frequency", "daily") or "daily"),
                target_days=data.get("target_days") or None,
                color=str(data.get("color", "#10b981") or "#10b981"),
                active=bool(data.get("active", True)),
            )

    def update(self, id: int, data: dict) -> Habit:
        with get_session() as session:
            repository = Repository(session, Habit)
            habit = repository.get_by_id(id)
            if habit is None:
                raise ValueError("Habito nao encontrado.")
            payload = {key: value for key, value in data.items() if key in {"name", "description", "frequency", "target_days", "color", "active"}}
            return repository.update(habit, **payload)

    def delete(self, id: int) -> None:
        with get_session() as session:
            repository = Repository(session, Habit)
            habit = repository.get_by_id(id)
            if habit is None:
                return
            repository.delete(habit)

    def restore(self, habit: Habit) -> None:
        with get_session() as session:
            restored = Habit(
                id=habit.id,
                name=habit.name,
                description=habit.description,
                frequency=habit.frequency,
                target_days=habit.target_days,
                color=habit.color,
                active=habit.active,
            )
            session.add(restored)
            session.flush()

    def log_today(self, habit_id: int, completed: bool, note: str = "") -> HabitLog:
        today = date.today()
        with get_session() as session:
            existing = session.scalar(select(HabitLog).where(HabitLog.habit_id == habit_id, HabitLog.date == today))
            repository = Repository(session, HabitLog)
            if existing is None:
                return repository.create(habit_id=habit_id, date=today, completed=completed, note=note or None)
            return repository.update(existing, completed=completed, note=note or None)

    def get_log(self, habit_id: int, date: date) -> HabitLog | None:
        with get_session() as session:
            return session.scalar(select(HabitLog).where(HabitLog.habit_id == habit_id, HabitLog.date == date))

    def get_logs_range(self, habit_id: int, start: date, end: date) -> list[HabitLog]:
        with get_session() as session:
            query = select(HabitLog).where(HabitLog.habit_id == habit_id, HabitLog.date >= start, HabitLog.date <= end)
            return list(session.scalars(query.order_by(HabitLog.date.asc())).all())

    def get_streak(self, habit_id: int) -> int:
        today = date.today()
        streak = 0
        cursor = today
        completed_days = {log.date for log in self.get_logs_range(habit_id, today - timedelta(days=365), today) if log.completed}
        while cursor in completed_days:
            streak += 1
            cursor -= timedelta(days=1)
        return streak

    def get_longest_streak(self, habit_id: int) -> int:
        logs = self.get_logs_range(habit_id, date.today() - timedelta(days=365), date.today())
        completed = sorted([log.date for log in logs if log.completed])
        if not completed:
            return 0
        longest = 1
        current = 1
        for idx in range(1, len(completed)):
            if completed[idx] == completed[idx - 1] + timedelta(days=1):
                current += 1
                longest = max(longest, current)
            else:
                current = 1
        return longest

    def get_completion_rate(self, habit_id: int, days: int = 30) -> float:
        end = date.today()
        start = end - timedelta(days=days - 1)
        logs = self.get_logs_range(habit_id, start, end)
        completed = sum(1 for log in logs if log.completed)
        return completed / max(days, 1)

    def get_heatmap_data(self, days: int = 365) -> dict:
        end_date = date.today()
        start_date = end_date - timedelta(days=max(days - 1, 0))
        with get_session() as session:
            habits = session.scalars(select(Habit).where(Habit.active.is_(True))).all()
            total = max(len(habits), 1)
            logs = session.scalars(
                select(HabitLog).where(HabitLog.date >= start_date, HabitLog.date <= end_date, HabitLog.completed.is_(True))
            ).all()
            completed_by_day: dict[date, int] = {}
            for log in logs:
                completed_by_day[log.date] = completed_by_day.get(log.date, 0) + 1
            return {day: min(value / total, 1.0) for day, value in completed_by_day.items()}

    def get_today_summary(self) -> dict:
        habits = self.get_all(active_only=True)
        total = len(habits)
        completed = 0
        for habit in habits:
            log = self.get_log(habit.id, date.today())
            if log and log.completed:
                completed += 1
        return {
            "total": total,
            "completed": completed,
            "rate": completed / max(total, 1),
        }
