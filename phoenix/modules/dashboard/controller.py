from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import func, select

from phoenix.core.database import get_session
from phoenix.core.models import Account, Book, FocusSession, Goal, Habit, HabitLog, HealthLog, Project, Task, Transaction
from phoenix.core.repository import Repository


class DashboardController:
    def summary(self) -> dict[str, int | float]:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        with get_session() as session:
            goals = Repository(session, Goal).list_all()
            active_goals = [goal for goal in goals if goal.status == "active"]
            completed_goals = [goal for goal in goals if goal.status == "completed"]
            accounts = Repository(session, Account).list_all()
            transactions = Repository(session, Transaction).list_all()
            balance = sum(account.initial_balance for account in accounts)
            balance += sum(tx.amount for tx in transactions if tx.type == "income")
            balance -= sum(tx.amount for tx in transactions if tx.type == "expense")
            best_streak = self._compute_best_streak(Repository(session, Habit).list_all())
            focus_count = session.scalar(
                select(func.count(FocusSession.id)).where(FocusSession.date >= week_start, FocusSession.date <= today)
            ) or 0
            return {
                "goals": len(goals),
                "goals_active": len(active_goals),
                "goals_completed_pct": int((len(completed_goals) / len(goals)) * 100) if goals else 0,
                "balance": round(balance, 2),
                "best_streak": best_streak,
                "focus_week": int(focus_count),
                "habits": len(Repository(session, Habit).list_all()),
                "transactions": len(transactions),
                "books": len(Repository(session, Book).list_all()),
                "projects": len(Repository(session, Project).list_all()),
                "tasks": len(Repository(session, Task).list_all()),
            }

    def monthly_cash_flow_last_six_months(self) -> tuple[list[str], list[float], list[float]]:
        today = date.today().replace(day=1)
        labels: list[str] = []
        incomes: list[float] = []
        expenses: list[float] = []
        with get_session() as session:
            transactions = Repository(session, Transaction).list_all()
            for offset in range(5, -1, -1):
                month_start = (today.replace(day=1) - timedelta(days=offset * 31)).replace(day=1)
                month_end = ((month_start + timedelta(days=32)).replace(day=1)) - timedelta(days=1)
                labels.append(month_start.strftime("%b/%y"))
                month_txs = [tx for tx in transactions if month_start <= tx.date <= month_end]
                incomes.append(round(sum(tx.amount for tx in month_txs if tx.type == "income"), 2))
                expenses.append(round(sum(tx.amount for tx in month_txs if tx.type == "expense"), 2))
        return labels, incomes, expenses

    def mood_energy_last_30_days(self) -> tuple[list[str], list[int], list[int]]:
        start = date.today() - timedelta(days=29)
        labels: list[str] = []
        mood: list[int] = []
        energy: list[int] = []
        with get_session() as session:
            logs = session.scalars(select(HealthLog).where(HealthLog.date >= start).order_by(HealthLog.date.asc())).all()
            by_date = {entry.date: entry for entry in logs}
            for index in range(30):
                current = start + timedelta(days=index)
                labels.append(current.strftime("%d/%m"))
                entry = by_date.get(current)
                mood.append(entry.mood or 0 if entry else 0)
                energy.append(entry.energy or 0 if entry else 0)
        return labels, mood, energy

    def upcoming_goals(self) -> list[Goal]:
        today = date.today()
        limit = today + timedelta(days=7)
        with get_session() as session:
            return list(
                session.scalars(
                    select(Goal)
                    .where(Goal.target_date.is_not(None), Goal.target_date >= today, Goal.target_date <= limit)
                    .order_by(Goal.target_date.asc())
                ).all()
            )

    def habits_for_today(self) -> list[dict[str, object]]:
        today = date.today()
        with get_session() as session:
            habits = session.scalars(select(Habit).where(Habit.active.is_(True)).order_by(Habit.created_at.asc())).all()
            logs = session.scalars(select(HabitLog).where(HabitLog.date == today)).all()
            by_habit = {log.habit_id: log for log in logs}
            return [
                {
                    "id": habit.id,
                    "name": habit.name,
                    "completed": bool(by_habit.get(habit.id) and by_habit[habit.id].completed),
                }
                for habit in habits
            ]

    def toggle_habit(self, habit_id: int, checked: bool) -> None:
        today = date.today()
        with get_session() as session:
            log = session.scalar(select(HabitLog).where(HabitLog.habit_id == habit_id, HabitLog.date == today))
            if log is None:
                log = HabitLog(habit_id=habit_id, date=today, completed=checked)
                session.add(log)
            else:
                log.completed = checked
            session.flush()

    def active_tasks(self) -> list[Task]:
        with get_session() as session:
            return list(
                session.scalars(
                    select(Task)
                    .where(Task.status.in_(["in_progress", "doing", "review"]))
                    .order_by(Task.updated_at.desc())
                ).all()
            )

    def _compute_best_streak(self, habits: list[Habit]) -> int:
        best = 0
        for habit in habits:
            completed_days = sorted(log.date for log in habit.logs if log.completed)
            streak = 0
            previous: date | None = None
            for current in completed_days:
                if previous and current == previous + timedelta(days=1):
                    streak += 1
                else:
                    streak = 1
                best = max(best, streak)
                previous = current
        return best
