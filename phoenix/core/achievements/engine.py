from __future__ import annotations

"""Engine de conquistas com avaliacao baseada em eventos."""

from PyQt6.QtCore import QObject, pyqtSignal


class AchievementEngine(QObject):
    """Acompanha progresso e desbloqueio de conquistas.

    Args:
        session: Sessao SQLAlchemy ativa.
        parent: Pai Qt opcional.
    """

    achievement_unlocked = pyqtSignal(dict)

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self._session = session
        self._ensure_catalog()

    def _ensure_catalog(self) -> None:
        """Insere no banco conquistas ausentes do catalogo."""

        from phoenix.core.achievements.catalog import CATALOG
        from phoenix.core.models import Achievement

        existing = {row[0] for row in self._session.query(Achievement.key).all()}
        new_rows = [Achievement(**item) for item in CATALOG if item["key"] not in existing]
        if new_rows:
            self._session.bulk_save_objects(new_rows)
            self._session.commit()

    def check(self, event_type: str, data: dict) -> None:
        """Avalia conquistas com base no tipo de evento.

        Args:
            event_type: Nome do evento ocorrido.
            data: Carga util do evento.
        """

        handlers = {
            "habit_check": self._check_habit_achievements,
            "goal_complete": self._check_goal_achievements,
            "transaction_save": self._check_finance_achievements,
            "focus_complete": self._check_focus_achievements,
            "diary_save": self._check_diary_achievements,
            "module_visit": self._check_general_achievements,
            "app_start": self._check_general_achievements,
        }
        handler = handlers.get(event_type)
        if handler:
            handler(data)

    def _unlock(self, key: str) -> None:
        from phoenix.core.models import Achievement, UserAchievement

        ach = self._session.query(Achievement).filter_by(key=key).first()
        if not ach:
            return
        existing = self._session.query(UserAchievement).filter_by(achievement_id=ach.id).first()
        if existing:
            return
        unlocked = UserAchievement(achievement_id=ach.id, progress=1.0, notified=False)
        self._session.add(unlocked)
        self._session.commit()
        self.achievement_unlocked.emit(
            {
                "name": ach.name,
                "icon": ach.icon,
                "xp": ach.xp_reward,
                "rarity": ach.rarity,
                "description": ach.description,
            }
        )

    def _check_habit_achievements(self, data: dict) -> None:
        from phoenix.core.models import Habit, HabitLog
        from phoenix.core.native_bridge import calculate_streak

        habit_id = data.get("habit_id")
        total_logs = self._session.query(HabitLog).count()
        if total_logs >= 1:
            self._unlock("habit_first")

        if habit_id is not None:
            logs = self._session.query(HabitLog).filter_by(habit_id=habit_id).all()
            streak = calculate_streak([str(log.date) for log in logs])
            if streak >= 7:
                self._unlock("habit_week")
            if streak >= 30:
                self._unlock("habit_month")

        active_habits = self._session.query(Habit).filter_by(active=True).count()
        if active_habits >= 5:
            self._unlock("habit_multi")

    def _check_goal_achievements(self, data: dict) -> None:
        if data.get("created"):
            self._unlock("goal_first")
        if data.get("completed"):
            self._unlock("goal_complete")

    def _check_finance_achievements(self, data: dict) -> None:
        from phoenix.core.models import Transaction

        total = self._session.query(Transaction).count()
        if total >= 100:
            self._unlock("fin_100tx")
        if data.get("imported"):
            self._unlock("fin_import")

    def _check_focus_achievements(self, data: dict) -> None:
        if data.get("duration_min", 0) >= 90:
            self._unlock("focus_first")

    def _check_diary_achievements(self, data: dict) -> None:
        if data.get("created"):
            self._unlock("diary_first")

    def _check_general_achievements(self, data: dict) -> None:
        if data.get("onboarded"):
            self._unlock("gen_onboard")

    def get_progress(self, key: str) -> float:
        from phoenix.core.models import Achievement, UserAchievement

        achievement = self._session.query(Achievement).filter_by(key=key).first()
        if not achievement:
            return 0.0
        unlocked = self._session.query(UserAchievement).filter_by(achievement_id=achievement.id).first()
        return float(unlocked.progress) if unlocked else 0.0

    def get_total_xp(self) -> int:
        from phoenix.core.models import Achievement, UserAchievement

        unlocked = (
            self._session.query(Achievement.xp_reward)
            .join(UserAchievement, Achievement.id == UserAchievement.achievement_id)
            .all()
        )
        return int(sum(row[0] for row in unlocked))

    def get_level(self) -> tuple[int, str]:
        xp = self.get_total_xp()
        levels = [
            (0, "Iniciante"),
            (500, "Explorador"),
            (1500, "Comprometido"),
            (3000, "Dedicado"),
            (6000, "Focado"),
            (10000, "Mestre"),
            (20000, "Lendario"),
        ]
        for threshold, name in reversed(levels):
            if xp >= threshold:
                return levels.index((threshold, name)) + 1, name
        return 1, "Iniciante"
