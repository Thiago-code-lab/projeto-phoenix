from __future__ import annotations

from sqlalchemy import or_, select

from phoenix.core.database import get_session
from phoenix.core.models import Note
from phoenix.core.repository import Repository


class NotesController:
    def list_notes(self) -> list[Note]:
        with get_session() as session:
            return list(session.scalars(select(Note).order_by(Note.updated_at.desc())).all())

    def search_notes(self, term: str) -> list[Note]:
        with get_session() as session:
            if not term:
                return self.list_notes()
            return list(
                session.scalars(
                    select(Note).where(or_(Note.title.ilike(f"%{term}%"), Note.content.ilike(f"%{term}%"))).order_by(Note.updated_at.desc())
                ).all()
            )

    def save_note(self, note_id: int | None, title: str, content: str, parent_id: int | None = None) -> Note:
        with get_session() as session:
            repository = Repository(session, Note)
            if note_id is None:
                return repository.add(title=title or "Nova nota", content=content, parent_id=parent_id)
            note = repository.get(note_id)
            if note is None:
                return repository.add(title=title or "Nova nota", content=content, parent_id=parent_id)
            note.title = title or note.title
            note.content = content
            note.parent_id = parent_id
            session.add(note)
            session.flush()
            return note

    def backlinks(self, note_id: int) -> list[Note]:
        with get_session() as session:
            note = Repository(session, Note).get(note_id)
            if note is None or not note.title:
                return []
            return list(
                session.scalars(select(Note).where(Note.id != note_id, Note.content.ilike(f"%{note.title}%"))).all()
            )
