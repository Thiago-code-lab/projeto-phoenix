from __future__ import annotations

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from phoenix.core.database import get_session
from phoenix.core.models import Goal, GoalMilestone
from phoenix.core.repository import Repository


class GoalsController:
    def get_all(self, status: str | None = None, category: str | None = None) -> list[Goal]:
        with get_session() as session:
            query = select(Goal).options(selectinload(Goal.milestones)).order_by(Goal.target_date.asc().nullslast(), Goal.created_at.desc())
            if status and status != "all":
                query = query.where(Goal.status == status)
            if category and category != "all":
                query = query.where(Goal.category == category)
            return list(session.scalars(query).all())

    def get_by_id(self, id: int) -> Goal | None:
        with get_session() as session:
            return session.scalar(select(Goal).options(selectinload(Goal.milestones)).where(Goal.id == id))

    def create(self, data: dict) -> Goal:
        title = str(data.get("title", "")).strip()
        if not title:
            raise ValueError("Titulo e obrigatorio.")

        with get_session() as session:
            repository = Repository(session, Goal)
            return repository.create(
                title=title,
                description=str(data.get("description", "")).strip() or None,
                category=str(data.get("category", "")).strip() or "geral",
                status=str(data.get("status", "active")),
                target_value=self._to_float(data.get("target_value")),
                current_value=float(self._to_float(data.get("current_value"), default=0.0) or 0.0),
                unit=str(data.get("unit", "")).strip() or None,
                start_date=self._to_date(data.get("start_date")),
                target_date=self._to_date(data.get("target_date")),
                color=str(data.get("color", "#6366f1")) or "#6366f1",
            )

    def update(self, id: int, data: dict) -> Goal:
        with get_session() as session:
            repository = Repository(session, Goal)
            goal = repository.get_by_id(id)
            if goal is None:
                raise ValueError("Meta nao encontrada.")
            values: dict[str, object] = {}
            for key in [
                "title",
                "description",
                "category",
                "status",
                "unit",
                "color",
                "target_value",
                "current_value",
                "start_date",
                "target_date",
            ]:
                if key not in data:
                    continue
                value = data[key]
                if key in {"target_value", "current_value"}:
                    values[key] = self._to_float(value, default=0.0)
                elif key in {"start_date", "target_date"}:
                    values[key] = self._to_date(value)
                else:
                    values[key] = value
            return repository.update(goal, **values)

    def delete(self, id: int) -> None:
        with get_session() as session:
            repository = Repository(session, Goal)
            goal = repository.get_by_id(id)
            if goal is None:
                return
            repository.delete(goal)

    def restore(self, goal: Goal) -> None:
        with get_session() as session:
            payload = {
                "id": goal.id,
                "title": goal.title,
                "description": goal.description,
                "category": goal.category,
                "status": goal.status,
                "target_value": goal.target_value,
                "current_value": goal.current_value,
                "unit": goal.unit,
                "start_date": goal.start_date,
                "target_date": goal.target_date,
                "color": goal.color,
            }
            restored = Goal(**payload)
            session.add(restored)
            session.flush()
            for milestone in goal.milestones:
                session.add(
                    GoalMilestone(
                        goal_id=restored.id,
                        title=milestone.title,
                        completed=milestone.completed,
                        due_date=milestone.due_date,
                    )
                )
            session.flush()

    def get_summary(self) -> dict:
        with get_session() as session:
            goals = list(session.scalars(select(Goal)).all())
            active = [goal for goal in goals if goal.status == "active"]
            completed = [goal for goal in goals if goal.status == "completed"]
            progress_values = [self._progress(goal) for goal in goals if goal.target_value and goal.target_value > 0]
            next_deadline = session.scalar(
                select(func.min(Goal.target_date)).where(Goal.status == "active", Goal.target_date.is_not(None))
            )
            return {
                "total_active": len(active),
                "total_completed": len(completed),
                "avg_progress": round(sum(progress_values) / len(progress_values), 2) if progress_values else 0.0,
                "next_deadline": next_deadline,
            }

    def add_milestone(self, goal_id: int, data: dict) -> GoalMilestone:
        title = str(data.get("title", "")).strip()
        if not title:
            raise ValueError("Titulo do milestone e obrigatorio.")
        with get_session() as session:
            goal = Repository(session, Goal).get_by_id(goal_id)
            if goal is None:
                raise ValueError("Meta nao encontrada para milestone.")
            return Repository(session, GoalMilestone).create(
                goal_id=goal_id,
                title=title,
                completed=bool(data.get("completed", False)),
                due_date=self._to_date(data.get("due_date")),
            )

    def toggle_milestone(self, milestone_id: int) -> GoalMilestone:
        with get_session() as session:
            repository = Repository(session, GoalMilestone)
            milestone = repository.get_by_id(milestone_id)
            if milestone is None:
                raise ValueError("Milestone nao encontrado.")
            return repository.update(milestone, completed=not milestone.completed)

    def delete_milestone(self, milestone_id: int) -> None:
        with get_session() as session:
            repository = Repository(session, GoalMilestone)
            milestone = repository.get_by_id(milestone_id)
            if milestone is None:
                return
            repository.delete(milestone)

    def _to_float(self, value: object, default: float | None = None) -> float | None:
        if value in (None, ""):
            return default
        return float(str(value).replace(",", "."))

    def _to_date(self, value: object) -> date | None:
        if value in (None, ""):
            return None
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value))

    def _progress(self, goal: Goal) -> float:
        target = goal.target_value or 0.0
        if target <= 0:
            return 0.0
        return min(max(goal.current_value / target, 0.0), 1.0)
