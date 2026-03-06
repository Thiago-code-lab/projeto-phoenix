from __future__ import annotations

"""Configuracao do banco local SQLite do Phoenix."""

import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

LOGGER = logging.getLogger(__name__)

DATABASE_PATH = Path(__file__).resolve().parents[1] / "phoenix.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH.as_posix()}"


class Base(DeclarativeBase):
    """Base declarativa para todos os modelos ORM."""

    pass


engine = create_engine(
    DATABASE_URL,
    future=True,
    echo=False,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


@contextmanager
def get_session() -> Iterator[Session]:
    """Abre uma sessao transacional protegida com commit e rollback."""

    init_database()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        LOGGER.exception("Falha durante operacao de banco")
        raise
    finally:
        session.close()


def init_database() -> None:
    """Cria o schema ORM na primeira execucao."""

    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
