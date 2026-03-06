from __future__ import annotations

from dynaconf import Dynaconf

from phoenix.core.database import get_session
from phoenix.core.database import DATABASE_PATH
from phoenix.core.models import Review
from phoenix.core.repository import Repository

SETTINGS = Dynaconf(settings_files=[str(DATABASE_PATH.parent / "settings.toml")])


class ReviewsController:
    def list_reviews(self) -> list[Review]:
        with get_session() as session:
            return Repository(session, Review).list_all()

    def latest_scores(self) -> tuple[list[str], list[float], list[float] | None]:
        areas = list(SETTINGS.get("review.areas", []))
        reviews = self.list_reviews()
        if not reviews:
            return areas, [6.0 for _ in areas], None
        current = reviews[-1].scores or {}
        previous = reviews[-2].scores if len(reviews) > 1 else None
        current_values = [float(current.get(area, 0)) for area in areas]
        previous_values = [float(previous.get(area, 0)) for area in areas] if previous else None
        return areas, current_values, previous_values
