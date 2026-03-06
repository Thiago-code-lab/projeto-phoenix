from __future__ import annotations

from datetime import date

from sqlalchemy import extract, func, select

from phoenix.core.database import get_session
from phoenix.core.models import Book
from phoenix.core.repository import Repository


class LibraryController:
    def get_all(self, status: str | None = None, genre: str | None = None, search: str | None = None) -> list[Book]:
        with get_session() as session:
            query = select(Book).order_by(Book.created_at.desc())
            if status and status != "all":
                query = query.where(Book.status == status)
            if genre and genre != "all":
                query = query.where(Book.genre == genre)
            if search:
                term = f"%{search}%"
                query = query.where((Book.title.ilike(term)) | (Book.author.ilike(term)))
            return list(session.scalars(query).all())

    def create(self, data: dict) -> Book:
        title = str(data.get("title", "")).strip()
        if not title:
            raise ValueError("Titulo e obrigatorio.")
        with get_session() as session:
            return Repository(session, Book).create(
                title=title,
                author=str(data.get("author", "")).strip() or None,
                genre=str(data.get("genre", "")).strip() or None,
                pages=self._as_int(data.get("pages")),
                pages_read=self._as_int(data.get("pages_read"), 0) or 0,
                status=str(data.get("status", "wishlist") or "wishlist"),
                rating=self._as_float(data.get("rating")),
                start_date=self._as_date(data.get("start_date")),
                end_date=self._as_date(data.get("end_date")),
                notes=str(data.get("notes", "")).strip() or None,
                tags=data.get("tags"),
            )

    def update(self, id: int, data: dict) -> Book:
        with get_session() as session:
            repository = Repository(session, Book)
            book = repository.get_by_id(id)
            if book is None:
                raise ValueError("Livro nao encontrado.")
            payload: dict[str, object] = {}
            for key in ["title", "author", "genre", "status", "notes", "tags"]:
                if key in data:
                    payload[key] = data[key]
            if "pages" in data:
                payload["pages"] = self._as_int(data.get("pages"))
            if "pages_read" in data:
                payload["pages_read"] = self._as_int(data.get("pages_read"), 0) or 0
            if "rating" in data:
                payload["rating"] = self._as_float(data.get("rating"))
            if "start_date" in data:
                payload["start_date"] = self._as_date(data.get("start_date"))
            if "end_date" in data:
                payload["end_date"] = self._as_date(data.get("end_date"))
            return repository.update(book, **payload)

    def delete(self, id: int) -> None:
        with get_session() as session:
            repository = Repository(session, Book)
            book = repository.get_by_id(id)
            if book is None:
                return
            repository.delete(book)

    def restore(self, book: Book) -> None:
        with get_session() as session:
            session.add(
                Book(
                    id=book.id,
                    title=book.title,
                    author=book.author,
                    genre=book.genre,
                    pages=book.pages,
                    pages_read=book.pages_read,
                    status=book.status,
                    rating=book.rating,
                    start_date=book.start_date,
                    end_date=book.end_date,
                    notes=book.notes,
                    tags=book.tags,
                )
            )
            session.flush()

    def update_progress(self, book_id: int, pages_read: int) -> Book:
        with get_session() as session:
            repository = Repository(session, Book)
            book = repository.get_by_id(book_id)
            if book is None:
                raise ValueError("Livro nao encontrado.")
            target = max(book.pages or pages_read, 1)
            progress = min(max(pages_read, 0), target)
            status = "completed" if progress >= target else ("reading" if progress > 0 else book.status)
            if status == "completed" and not book.end_date:
                return repository.update(book, pages_read=progress, status=status, end_date=date.today())
            return repository.update(book, pages_read=progress, status=status)

    def get_stats(self) -> dict:
        today = date.today()
        with get_session() as session:
            books = list(session.scalars(select(Book)).all())
            total = len(books)
            reading = sum(1 for book in books if book.status == "reading")
            completed_year = sum(1 for book in books if book.status == "completed" and book.end_date and book.end_date.year == today.year)
            pages_read_year = sum(book.pages_read for book in books if book.start_date and book.start_date.year == today.year)
            ratings = [book.rating for book in books if book.rating is not None]
            avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else 0.0

            genre_distribution: dict[str, int] = {}
            for book in books:
                label = book.genre or "Sem genero"
                genre_distribution[label] = genre_distribution.get(label, 0) + 1

            books_per_month = {
                int(month): int(count)
                for month, count in session.execute(
                    select(extract("month", Book.created_at), func.count(Book.id)).where(extract("year", Book.created_at) == today.year).group_by(extract("month", Book.created_at))
                ).all()
            }

            return {
                "total": total,
                "reading": reading,
                "completed_year": completed_year,
                "pages_read_year": pages_read_year,
                "avg_rating": avg_rating,
                "genre_distribution": genre_distribution,
                "books_per_month": books_per_month,
            }

    def _as_int(self, value: object, default: int | None = None) -> int | None:
        if value in (None, ""):
            return default
        return int(value)

    def _as_float(self, value: object, default: float | None = None) -> float | None:
        if value in (None, ""):
            return default
        return float(value)

    def _as_date(self, value: object) -> date | None:
        if value in (None, ""):
            return None
        if isinstance(value, date):
            return value
        return date.fromisoformat(str(value))
