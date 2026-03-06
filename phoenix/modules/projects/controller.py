from __future__ import annotations

from sqlalchemy import select

from phoenix.core.database import get_session
from phoenix.core.models import Project, Task
from phoenix.core.repository import Repository


class ProjectsController:
    def get_all_projects(self) -> list[Project]:
        with get_session() as session:
            return list(session.scalars(select(Project).order_by(Project.created_at.desc())).all())

    def create_project(self, data: dict) -> Project:
        name = str(data.get("name", "")).strip()
        if not name:
            raise ValueError("Nome do projeto e obrigatorio.")
        with get_session() as session:
            return Repository(session, Project).create(
                name=name,
                description=str(data.get("description", "")).strip() or None,
                color=str(data.get("color", "#8b5cf6") or "#8b5cf6"),
                status=str(data.get("status", "active") or "active"),
                start_date=data.get("start_date"),
                end_date=data.get("end_date"),
            )

    def update_project(self, id: int, data: dict) -> Project:
        with get_session() as session:
            repository = Repository(session, Project)
            project = repository.get_by_id(id)
            if project is None:
                raise ValueError("Projeto nao encontrado.")
            payload = {key: value for key, value in data.items() if key in {"name", "description", "color", "status", "start_date", "end_date"}}
            return repository.update(project, **payload)

    def delete_project(self, id: int) -> None:
        with get_session() as session:
            repository = Repository(session, Project)
            project = repository.get_by_id(id)
            if project is None:
                return
            repository.delete(project)

    def restore_project(self, project: Project) -> None:
        with get_session() as session:
            session.add(
                Project(
                    id=project.id,
                    name=project.name,
                    description=project.description,
                    color=project.color,
                    status=project.status,
                    start_date=project.start_date,
                    end_date=project.end_date,
                )
            )
            session.flush()

    def get_tasks(self, project_id: int, status: str | None = None) -> list[Task]:
        with get_session() as session:
            query = select(Task).where(Task.project_id == project_id)
            if status:
                query = query.where(Task.status == status)
            query = query.order_by(Task.status.asc(), Task.position.asc(), Task.updated_at.desc())
            return list(session.scalars(query).all())

    def create_task(self, data: dict) -> Task:
        title = str(data.get("title", "")).strip()
        if not title:
            raise ValueError("Titulo da tarefa e obrigatorio.")
        status = str(data.get("status", "backlog") or "backlog")
        project_id = int(data.get("project_id")) if data.get("project_id") else None
        with get_session() as session:
            last_position = (
                session.scalar(
                    select(Task.position)
                    .where(Task.project_id == project_id, Task.status == status)
                    .order_by(Task.position.desc())
                )
                or 0
            )
            return Repository(session, Task).create(
                project_id=project_id,
                title=title,
                description=str(data.get("description", "")).strip() or None,
                status=status,
                priority=str(data.get("priority", "medium") or "medium"),
                due_date=data.get("due_date"),
                tags=data.get("tags") or None,
                position=last_position + 1,
            )

    def update_task(self, id: int, data: dict) -> Task:
        with get_session() as session:
            repository = Repository(session, Task)
            task = repository.get_by_id(id)
            if task is None:
                raise ValueError("Tarefa nao encontrada.")
            payload = {key: value for key, value in data.items() if key in {"title", "description", "status", "priority", "due_date", "tags", "position", "project_id"}}
            return repository.update(task, **payload)

    def move_task(self, task_id: int, new_status: str, new_position: int) -> Task:
        with get_session() as session:
            repository = Repository(session, Task)
            task = repository.get_by_id(task_id)
            if task is None:
                raise ValueError("Tarefa nao encontrada.")

            siblings = list(
                session.scalars(
                    select(Task)
                    .where(Task.project_id == task.project_id, Task.status == new_status, Task.id != task_id)
                    .order_by(Task.position.asc())
                ).all()
            )
            clamped = max(0, min(new_position, len(siblings)))
            siblings.insert(clamped, task)
            for idx, item in enumerate(siblings):
                item.status = new_status
                item.position = idx
                session.add(item)
            session.flush()
            return task

    def delete_task(self, id: int) -> None:
        with get_session() as session:
            repository = Repository(session, Task)
            task = repository.get_by_id(id)
            if task is None:
                return
            repository.delete(task)

    def restore_task(self, task: Task) -> None:
        with get_session() as session:
            session.add(
                Task(
                    id=task.id,
                    project_id=task.project_id,
                    title=task.title,
                    description=task.description,
                    status=task.status,
                    priority=task.priority,
                    due_date=task.due_date,
                    tags=task.tags,
                    position=task.position,
                )
            )
            session.flush()

    def get_active_tasks(self) -> list[Task]:
        with get_session() as session:
            query = select(Task).where(Task.status != "done").order_by(Task.updated_at.desc())
            return list(session.scalars(query).all())

    def get_task_stats(self, project_id: int) -> dict:
        tasks = self.get_tasks(project_id)
        by_status: dict[str, int] = {}
        for task in tasks:
            by_status[task.status] = by_status.get(task.status, 0) + 1
        done = by_status.get("done", 0)
        total = len(tasks)
        return {
            "total": total,
            "done": done,
            "in_progress": by_status.get("in_progress", 0),
            "completion_rate": done / max(total, 1),
            "by_status": by_status,
        }
