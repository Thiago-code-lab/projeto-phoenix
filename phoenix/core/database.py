from __future__ import annotations

"""Configuracao do banco local SQLite do Phoenix."""

from functools import wraps
import logging
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Iterator, TypeVar

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import QueuePool

from phoenix.core.exceptions import DatabaseError

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
    poolclass=QueuePool,
    pool_pre_ping=True,
    pool_size=8,
    max_overflow=16,
    pool_recycle=1800,
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
    _patch_legacy_schema()


def _patch_legacy_schema() -> None:
    """Aplica ajustes incrementais em bancos SQLite legados."""

    with engine.begin() as connection:
        columns = {
            row[1]
            for row in connection.execute(text("PRAGMA table_info('focus_sessions');")).fetchall()
        }
        if "task_id" not in columns:
            connection.execute(text("ALTER TABLE focus_sessions ADD COLUMN task_id INTEGER"))


def run_integrity_check() -> None:
    """Executa o PRAGMA integrity_check e falha se o retorno nao for OK."""

    try:
        with engine.connect() as connection:
            result = connection.execute(text("PRAGMA integrity_check;")).scalar()
        if str(result).lower() != "ok":
            raise DatabaseError(f"Integridade do banco invalida: {result}")
    except SQLAlchemyError as exc:
        LOGGER.exception("Falha no health check do banco")
        raise DatabaseError("Falha ao verificar integridade do banco") from exc


def database_size_mb() -> float:
    """Retorna o tamanho atual do arquivo SQLite em MB."""

    if not DATABASE_PATH.exists():
        return 0.0
    return round(DATABASE_PATH.stat().st_size / (1024 * 1024), 2)


FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def db_operation(func: FuncT) -> FuncT:
    """Aplica tratamento padrao para metodos de acesso ao banco.

    O rollback transacional permanece centralizado em ``get_session``.
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return func(*args, **kwargs)
        except DatabaseError:
            raise
        except Exception as exc:  # noqa: BLE001
            LOGGER.exception("Falha em operacao de banco: %s", func.__qualname__)
            raise DatabaseError(f"Erro em operacao de banco: {func.__qualname__}") from exc

    return wrapper  # type: ignore[return-value]


def db_operation_class(cls: type[Any]) -> type[Any]:
    """Decora metodos publicos da classe com ``db_operation`` automaticamente."""

    for attr_name, attr_value in list(vars(cls).items()):
        if attr_name.startswith("_") or not callable(attr_value):
            continue
        setattr(cls, attr_name, db_operation(attr_value))
    return cls
