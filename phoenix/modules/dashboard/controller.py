from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import func, select

from phoenix.core.cache import LRUCache
from phoenix.core.database import db_operation_class, get_session
from phoenix.core.models import (
    Account,
    Book,
    FocusSession,
    Goal,
    GoalMilestone,
    Habit,
    HabitLog,
    HealthLog,
    JournalEntry,
    Project,
    Task,
    Transaction,
)
from phoenix.core.repository import Repository


@db_operation_class
class DashboardController:
    _lru_cache: LRUCache[object] = LRUCache(max_size=64)

    def summary(self) -> dict[str, int | float]:
        cache_key = f"summary:{date.today().isoformat()}"
        cached = self._lru_cache.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]

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
            payload = {
                "goals": len(goals),
                "goals_active": len(active_goals),
                "goals_completed_pct": int((len(completed_goals) / len(goals)) * 100) if goals else 0,
                "balance": round(balance, 2),
                "best_streak": best_streak,
                "global_streak": self.global_streak(),
                "focus_week": int(focus_count),
                "habits": len(Repository(session, Habit).list_all()),
                "transactions": len(transactions),
                "books": len(Repository(session, Book).list_all()),
                "projects": len(Repository(session, Project).list_all()),
                "tasks": len(Repository(session, Task).list_all()),
            }
            self._lru_cache.set(cache_key, payload)
            return payload

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
        cache_key = f"habits_today:{today.isoformat()}"
        cached = self._lru_cache.get(cache_key)
        if cached is not None:
            return cached  # type: ignore[return-value]
        with get_session() as session:
            habits = session.scalars(select(Habit).where(Habit.active.is_(True)).order_by(Habit.created_at.asc())).all()
            logs = session.scalars(select(HabitLog).where(HabitLog.date == today)).all()
            by_habit = {log.habit_id: log for log in logs}
            payload = [
                {
                    "id": habit.id,
                    "name": habit.name,
                    "completed": bool(by_habit.get(habit.id) and by_habit[habit.id].completed),
                }
                for habit in habits
            ]
            self._lru_cache.set(cache_key, payload)
            return payload

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
        self._lru_cache.invalidate("summary:")
        self._lru_cache.invalidate("habits_today:")

    def active_tasks(self) -> list[Task]:
        with get_session() as session:
            return list(
                session.scalars(
                    select(Task)
                    .where(Task.status.in_(["in_progress", "doing", "review"]))
                    .order_by(Task.updated_at.desc())
                ).all()
            )

    def daily_overview(self) -> dict[str, object]:
        """Resumo do dia com habitos pendentes, foco e tarefas de hoje."""

        today = date.today()
        habits = self.habits_for_today()
        pending_habits = [item["name"] for item in habits if not item["completed"]]
        with get_session() as session:
            focus_minutes = sum(
                session.scalars(select(FocusSession.duration_min).where(FocusSession.date == today, FocusSession.completed.is_(True))).all()
            )
            tasks_today = list(
                session.scalars(
                    select(Task)
                    .where(Task.due_date == today)
                    .order_by(Task.priority.asc(), Task.updated_at.desc())
                ).all()
            )
        return {
            "pending_habits": pending_habits,
            "focus_hours": round(focus_minutes / 60.0, 2),
            "tasks_today": tasks_today,
        }

    def weekly_productivity(self) -> tuple[list[str], list[float]]:
        """Retorna produtividade semanal combinando foco, habitos e tarefas concluídas."""

        today = date.today()
        start = today - timedelta(days=today.weekday())
        labels: list[str] = []
        scores: list[float] = []
        with get_session() as session:
            focus_sessions = list(session.scalars(select(FocusSession).where(FocusSession.date >= start, FocusSession.date <= today)).all())
            habit_logs = list(session.scalars(select(HabitLog).where(HabitLog.date >= start, HabitLog.date <= today, HabitLog.completed.is_(True))).all())
            done_tasks = list(session.scalars(select(Task).where(Task.updated_at >= datetime.combine(start, datetime.min.time()), Task.status == "done")).all())

        for offset in range(7):
            current = start + timedelta(days=offset)
            labels.append(current.strftime("%a"))
            focus_points = sum(item.duration_min for item in focus_sessions if item.date == current) / 25.0
            habit_points = sum(1 for item in habit_logs if item.date == current)
            task_points = sum(1 for item in done_tasks if item.updated_at.date() == current)
            scores.append(round(focus_points + habit_points + task_points, 2))
        return labels, scores

    def global_streak(self) -> int:
        """Streak global de dias com ao menos um check em qualquer modulo."""

        with get_session() as session:
            days = {item.date for item in session.scalars(select(HabitLog).where(HabitLog.completed.is_(True))).all()}
            days.update(item.date for item in session.scalars(select(FocusSession).where(FocusSession.completed.is_(True))).all())
            days.update(item for item in session.scalars(select(JournalEntry.date)).all())
        streak = 0
        cursor = date.today()
        while cursor in days:
            streak += 1
            cursor -= timedelta(days=1)
        return streak

    def upcoming_milestones(self, limit: int = 6) -> list[dict[str, object]]:
        """Lista milestones proximos com contagem regressiva em dias."""

        today = date.today()
        with get_session() as session:
            rows = list(
                session.scalars(
                    select(GoalMilestone)
                    .where(GoalMilestone.completed.is_(False), GoalMilestone.due_date.is_not(None), GoalMilestone.due_date >= today)
                    .order_by(GoalMilestone.due_date.asc())
                    .limit(limit)
                ).all()
            )
            goals = {goal.id: goal.title for goal in session.scalars(select(Goal)).all()}
        return [
            {
                "title": row.title,
                "goal": goals.get(row.goal_id, "Meta"),
                "days_left": (row.due_date - today).days if row.due_date else None,
            }
            for row in rows
        ]

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
