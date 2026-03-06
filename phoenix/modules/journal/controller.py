from __future__ import annotations

from datetime import date

from sqlalchemy import select

from phoenix.core.database import get_session
from phoenix.core.models import JournalEntry
from phoenix.core.repository import Repository


class JournalController:
    def get_entries(self, month: date | None = None, search: str | None = None, tags: list[str] | None = None) -> list[JournalEntry]:
        with get_session() as session:
            query = select(JournalEntry).order_by(JournalEntry.date.desc())
            if month is not None:
                start = month.replace(day=1)
                if month.month == 12:
                    end = month.replace(year=month.year + 1, month=1, day=1)
                else:
                    end = month.replace(month=month.month + 1, day=1)
                query = query.where(JournalEntry.date >= start, JournalEntry.date < end)
            if search:
                term = f"%{search}%"
                query = query.where((JournalEntry.title.ilike(term)) | (JournalEntry.content.ilike(term)))
            entries = list(session.scalars(query).all())
            if tags:
                entries = [entry for entry in entries if entry.tags and set(tags).issubset(set(entry.tags))]
            return entries

    def get_by_date(self, date: date) -> JournalEntry | None:
        with get_session() as session:
            return session.scalar(select(JournalEntry).where(JournalEntry.date == date))

    def create(self, data: dict) -> JournalEntry:
        content = str(data.get("content", "")).strip()
        if not content:
            raise ValueError("Conteudo e obrigatorio.")
        with get_session() as session:
            return Repository(session, JournalEntry).create(
                date=data.get("date", date.today()),
                title=str(data.get("title", "")).strip() or None,
                content=content,
                mood=int(data.get("mood")) if data.get("mood") not in (None, "") else None,
                tags=data.get("tags") or None,
            )

    def update(self, id: int, data: dict) -> JournalEntry:
        with get_session() as session:
            repository = Repository(session, JournalEntry)
            entry = repository.get_by_id(id)
            if entry is None:
                raise ValueError("Entrada nao encontrada.")
            payload: dict[str, object] = {}
            for key in ["title", "content", "tags", "date"]:
                if key in data:
                    payload[key] = data[key]
            if "mood" in data:
                payload["mood"] = int(data["mood"]) if data["mood"] not in (None, "") else None
            return repository.update(entry, **payload)

    def delete(self, id: int) -> None:
        with get_session() as session:
            repository = Repository(session, JournalEntry)
            entry = repository.get_by_id(id)
            if entry is None:
                return
            repository.delete(entry)

    def restore(self, entry: JournalEntry) -> None:
        with get_session() as session:
            session.add(
                JournalEntry(
                    id=entry.id,
                    date=entry.date,
                    title=entry.title,
                    content=entry.content,
                    mood=entry.mood,
                    tags=entry.tags,
                )
            )
            session.flush()

    def get_all_tags(self) -> list[str]:
        tags: set[str] = set()
        for entry in self.get_entries():
            for tag in entry.tags or []:
                tags.add(tag)
        return sorted(tags)

    def get_streak(self) -> int:
        today = date.today()
        entry_days = {entry.date for entry in self.get_entries()}
        streak = 0
        cursor = today
        while cursor in entry_days:
            streak += 1
            cursor = cursor.fromordinal(cursor.toordinal() - 1)
        return streak

    def get_entries_calendar(self, year: int, month: int) -> dict:
        entries = self.get_entries(month=date(year, month, 1))
        result: dict[int, dict[str, bool | int | None]] = {}
        for entry in entries:
            result[entry.date.day] = {"has_entry": True, "mood": entry.mood}
        return result
