from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import func, select

from phoenix.core.database import get_session
from phoenix.core.models import HealthLog, Workout
from phoenix.core.repository import Repository


class HealthController:
    def get_log(self, date: date) -> HealthLog | None:
        with get_session() as session:
            return session.scalar(select(HealthLog).where(HealthLog.date == date))

    def upsert_log(self, date: date, data: dict) -> HealthLog:
        with get_session() as session:
            repository = Repository(session, HealthLog)
            existing = session.scalar(select(HealthLog).where(HealthLog.date == date))
            payload = {
                "weight_kg": self._to_float(data.get("weight_kg")),
                "sleep_hours": self._to_float(data.get("sleep_hours")),
                "water_ml": self._to_int(data.get("water_ml")),
                "mood": self._to_int(data.get("mood")),
                "energy": self._to_int(data.get("energy")),
                "steps": self._to_int(data.get("steps")),
                "note": str(data.get("note", "")).strip() or None,
            }
            if existing is None:
                return repository.create(date=date, **payload)
            return repository.update(existing, **payload)

    def get_logs_range(self, start: date, end: date) -> list[HealthLog]:
        with get_session() as session:
            query = select(HealthLog).where(HealthLog.date >= start, HealthLog.date <= end).order_by(HealthLog.date.asc())
            return list(session.scalars(query).all())

    def get_workouts(self, start: date, end: date) -> list[Workout]:
        with get_session() as session:
            query = select(Workout).where(Workout.date >= start, Workout.date <= end).order_by(Workout.date.desc())
            return list(session.scalars(query).all())

    def add_workout(self, data: dict) -> Workout:
        with get_session() as session:
            return Repository(session, Workout).create(
                date=data.get("date", date.today()),
                type=str(data.get("type", "")).strip() or None,
                duration=self._to_int(data.get("duration")),
                calories=self._to_int(data.get("calories")),
                note=str(data.get("note", "")).strip() or None,
            )

    def delete_workout(self, id: int) -> None:
        with get_session() as session:
            repository = Repository(session, Workout)
            workout = repository.get_by_id(id)
            if workout is None:
                return
            repository.delete(workout)

    def restore_workout(self, workout: Workout) -> None:
        with get_session() as session:
            session.add(
                Workout(
                    id=workout.id,
                    date=workout.date,
                    type=workout.type,
                    duration=workout.duration,
                    calories=workout.calories,
                    note=workout.note,
                )
            )
            session.flush()

    def get_weight_series(self, days: int = 90) -> list[tuple[date, float]]:
        return [(log.date, float(log.weight_kg)) for log in self._window(days) if log.weight_kg is not None]

    def get_sleep_series(self, days: int = 30) -> list[tuple[date, float]]:
        return [(log.date, float(log.sleep_hours)) for log in self._window(days) if log.sleep_hours is not None]

    def get_mood_series(self, days: int = 30) -> list[tuple[date, int]]:
        return [(log.date, int(log.mood)) for log in self._window(days) if log.mood is not None]

    def get_water_series(self, days: int = 30) -> list[tuple[date, int]]:
        return [(log.date, int(log.water_ml)) for log in self._window(days) if log.water_ml is not None]

    def get_weekly_workouts(self, weeks: int = 12) -> list[tuple[str, int]]:
        end = date.today()
        start = end - timedelta(weeks=weeks)
        with get_session() as session:
            rows = session.execute(
                select(func.strftime("%Y-W%W", Workout.date), func.count(Workout.id))
                .where(Workout.date >= start, Workout.date <= end)
                .group_by(func.strftime("%Y-W%W", Workout.date))
                .order_by(func.strftime("%Y-W%W", Workout.date))
            ).all()
            return [(str(label), int(count)) for label, count in rows]

    def get_today_summary(self) -> dict:
        log = self.get_log(date.today())
        workouts = self.get_workouts(date.today(), date.today())
        return {
            "water_ml": log.water_ml if log else 0,
            "steps": log.steps if log else 0,
            "sleep_hours": log.sleep_hours if log else 0.0,
            "workouts": len(workouts),
        }

    def _window(self, days: int) -> list[HealthLog]:
        end = date.today()
        start = end - timedelta(days=max(days - 1, 0))
        return self.get_logs_range(start, end)

    def _to_int(self, value: object, default: int | None = None) -> int | None:
        if value in (None, ""):
            return default
        return int(value)

    def _to_float(self, value: object, default: float | None = None) -> float | None:
        if value in (None, ""):
            return default
        return float(value)
