from __future__ import annotations

from dynaconf import Dynaconf

from phoenix.core.database import DATABASE_PATH, db_operation_class, get_session
from phoenix.core.models import Review
from phoenix.core.repository import Repository

SETTINGS = Dynaconf(settings_files=[str(DATABASE_PATH.parent / "settings.toml")])


@db_operation_class
class ReviewsController:
    def list_reviews(self) -> list[Review]:
        with get_session() as session:
            return Repository(session, Review).list_all()

    def create_review(self, payload: dict) -> Review:
        with get_session() as session:
            review = Repository(session, Review).create(**payload)
            session.flush()
            return review

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
