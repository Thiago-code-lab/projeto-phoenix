from __future__ import annotations

from datetime import date, timedelta

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


class AnalyticsController:
    """Agrega metricas e gera relatorio de vida."""

    def get_life_score(self, session) -> dict:
        return {
            "habits": self._habits_score(session),
            "finances": self._finances_score(session),
            "focus": self._focus_score(session),
            "goals": self._goals_score(session),
            "health": self._health_score(session),
            "diary": self._diary_score(session),
        }

    def _habits_score(self, session) -> float:
        from phoenix.core.models import Habit, HabitLog
        from phoenix.core.native_bridge import calculate_streak

        habits = session.query(Habit).filter_by(active=True).all()
        if not habits:
            return 0.0
        scores = []
        for habit in habits:
            logs = session.query(HabitLog).filter_by(habit_id=habit.id).all()
            streak = calculate_streak([str(log.date) for log in logs])
            scores.append(min(streak / 30 * 100, 100))
        return sum(scores) / len(scores)

    def _finances_score(self, session) -> float:
        from phoenix.core.models import Transaction

        today = date.today()
        month_start = today.replace(day=1)
        txs = session.query(Transaction).filter(Transaction.date >= month_start).all()
        income = sum(tx.amount for tx in txs if tx.type == "income")
        expense = sum(tx.amount for tx in txs if tx.type == "expense")
        if income == 0:
            return 50.0
        savings_rate = (income - expense) / income
        return max(0, min(savings_rate * 200, 100))

    def _focus_score(self, session) -> float:
        from phoenix.core.models import FocusSession

        week_ago = date.today() - timedelta(days=7)
        sessions = session.query(FocusSession).filter(FocusSession.date >= week_ago, FocusSession.completed.is_(True)).all()
        weekly_hours = sum(s.duration_min for s in sessions) / 60
        return min(weekly_hours / 20 * 100, 100)

    def _goals_score(self, session) -> float:
        from phoenix.core.models import Goal

        total = session.query(Goal).count()
        done = session.query(Goal).filter_by(status="completed").count()
        if total == 0:
            return 0.0
        return done / total * 100

    def _health_score(self, session) -> float:
        del session
        return 50.0

    def _diary_score(self, session) -> float:
        from phoenix.core.models import JournalEntry

        week_ago = date.today() - timedelta(days=7)
        entries = session.query(JournalEntry).filter(JournalEntry.created_at >= week_ago).count()
        return min(entries / 7 * 100, 100)

    def get_life_report_data(self, session, month: int, year: int) -> dict:
        from phoenix.core.models import FocusSession, Goal, JournalEntry, Task, Transaction

        start = date(year, month, 1)
        return {
            "period": f"{month:02d}/{year}",
            "goals_created": session.query(Goal).filter(Goal.created_at >= start).count(),
            "goals_done": session.query(Goal).filter(Goal.status == "completed", Goal.created_at >= start).count(),
            "income": sum(tx.amount for tx in session.query(Transaction).filter(Transaction.date >= start, Transaction.type == "income")),
            "expense": sum(tx.amount for tx in session.query(Transaction).filter(Transaction.date >= start, Transaction.type == "expense")),
            "focus_hours": sum(s.duration_min for s in session.query(FocusSession).filter(FocusSession.date >= start, FocusSession.completed.is_(True))) / 60,
            "diary_entries": session.query(JournalEntry).filter(JournalEntry.created_at >= start).count(),
            "tasks_done": session.query(Task).filter(Task.status == "done", Task.updated_at >= start).count(),
            "life_scores": self.get_life_score(session),
        }

    def generate_life_report(self, data: dict, output_path: str) -> str:
        pdf = canvas.Canvas(output_path, pagesize=A4)
        w, h = A4
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(40, h - 60, f"RELATORIO DE VIDA - {data.get('period', '-')}")
        pdf.setFont("Helvetica", 11)
        y = h - 100
        for key, value in data.items():
            if key == "life_scores":
                continue
            pdf.drawString(40, y, f"{key}: {value}")
            y -= 18
        pdf.drawString(40, 40, f"Phoenix 3.0 - Rebirth | Gerado em {date.today().isoformat()}")
        pdf.save()
        return output_path
