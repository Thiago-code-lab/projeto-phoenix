from __future__ import annotations

"""Bootstrap do schema inicial e seed minima do Phoenix."""

import logging

from sqlalchemy import inspect, select
from sqlalchemy.exc import SQLAlchemyError

from .database import engine
from .models import UserProfile

LOGGER = logging.getLogger(__name__)


def migrate_schema() -> None:
    """Executa migracao automatica baseada em metadata ORM."""

    from .database import Base
    from . import models  # noqa: F401

    try:
        Base.metadata.create_all(bind=engine)

        inspector = inspect(engine)
        tables = set(inspector.get_table_names())
        if "user_profile" not in tables:
            Base.metadata.create_all(bind=engine)

        with engine.begin() as connection:
            existing = connection.execute(select(UserProfile.id).limit(1)).first()
            if existing is None:
                connection.execute(
                    UserProfile.__table__.insert().values(
                        name="Usuario",
                        currency="BRL",
                        theme="dark",
                    )
                )
    except SQLAlchemyError:
        LOGGER.exception("Falha ao migrar schema inicial")
        raise
