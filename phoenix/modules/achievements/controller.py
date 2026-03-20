from __future__ import annotations

from sqlalchemy import select

from phoenix.core.database import db_operation_class, get_session
from phoenix.core.models import Achievement, UserAchievement


@db_operation_class
class AchievementsController:
    """Facade de leitura para o modulo de conquistas."""

    def list_all(self) -> list[dict[str, object]]:
        with get_session() as session:
            achievements = list(session.scalars(select(Achievement).order_by(Achievement.category, Achievement.name)).all())
            unlocked_ids = {
                row[0]
                for row in session.query(UserAchievement.achievement_id).all()
            }
            result: list[dict[str, object]] = []
            for ach in achievements:
                result.append(
                    {
                        "id": ach.id,
                        "key": ach.key,
                        "name": ach.name,
                        "description": ach.description,
                        "icon": ach.icon,
                        "category": ach.category,
                        "rarity": ach.rarity,
                        "xp_reward": ach.xp_reward,
                        "unlocked": ach.id in unlocked_ids,
                    }
                )
            return result
