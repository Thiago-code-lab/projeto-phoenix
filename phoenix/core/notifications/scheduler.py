from __future__ import annotations

from datetime import date, datetime, timedelta

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class ReminderScheduler(QObject):
    """Dispara lembretes periodicos sem bloquear a UI.

    Args:
        session: Sessao SQLAlchemy usada para consultas.
        parent: Pai Qt opcional.
    """

    reminder_triggered = pyqtSignal(str, str)

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self._session = session
        self._daily_timer = QTimer(self)
        self._daily_timer.timeout.connect(self._daily_check)
        self._daily_timer.start(3_600_000)

    def _daily_check(self) -> None:
        now = datetime.now()
        self._check_habit_reminders(now)
        self._check_goal_deadlines(now)
        self._check_focus_reminders(now)
        self._check_finance_reminders(now)

    def _check_habit_reminders(self, now: datetime) -> None:
        from phoenix.core.models import Habit, HabitLog

        today = date.today()
        habits = self._session.query(Habit).filter_by(active=True).all()
        for habit in habits:
            reminder_hour = getattr(habit, "reminder_hour", None)
            if reminder_hour is None:
                continue
            if now.hour == reminder_hour and now.minute < 5:
                checked_today = self._session.query(HabitLog).filter_by(habit_id=habit.id, date=today).first()
                if not checked_today:
                    self.reminder_triggered.emit(
                        f"Habito: {habit.name}",
                        "Voce ainda nao fez seu check de hoje.",
                    )

    def _check_goal_deadlines(self, now: datetime) -> None:
        from phoenix.core.models import GoalMilestone

        today = date.today()
        milestones = self._session.query(GoalMilestone).filter(
            GoalMilestone.due_date <= today + timedelta(days=3),
            GoalMilestone.completed.is_(False),
        ).all()
        for milestone in milestones:
            days = (milestone.due_date - today).days if milestone.due_date else 0
            self.reminder_triggered.emit(
                "Milestone se aproximando",
                f"{milestone.title} vence em {days} dia(s)",
            )

    def _check_finance_reminders(self, now: datetime) -> None:
        if now.day == 1 and now.hour == 9 and now.minute < 5:
            self.reminder_triggered.emit(
                "Fechamento mensal",
                "Hora de revisar seu extrato e fechar o mes financeiro.",
            )

    def _check_focus_reminders(self, now: datetime) -> None:
        del now
