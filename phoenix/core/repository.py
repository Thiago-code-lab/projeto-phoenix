from __future__ import annotations

"""Implementacao do repository pattern generico do Phoenix."""

import logging
from typing import Generic, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from .database import Base

ModelT = TypeVar("ModelT", bound=Base)
LOGGER = logging.getLogger(__name__)


class Repository(Generic[ModelT]):
    """Fornece CRUD generico baseado em SQLAlchemy ORM."""

    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def query(self) -> Select[tuple[ModelT]]:
        """Retorna uma consulta base para o modelo atual."""

        return select(self.model)

    def get_all(self) -> list[ModelT]:
        """Lista todas as entidades do modelo atual."""

        try:
            return list(self.session.scalars(self.query()).all())
        except SQLAlchemyError:
            LOGGER.exception("Falha ao listar entidades de %s", self.model.__name__)
            raise

    def list_all(self) -> list[ModelT]:
        """Alias retrocompativel para get_all."""

        return self.get_all()

    def get_by_id(self, entity_id: int) -> ModelT | None:
        """Busca uma entidade por identificador primario."""

        try:
            return self.session.get(self.model, entity_id)
        except SQLAlchemyError:
            LOGGER.exception("Falha ao buscar %s por id=%s", self.model.__name__, entity_id)
            raise

    def get(self, entity_id: int) -> ModelT | None:
        """Alias retrocompativel para get_by_id."""

        return self.get_by_id(entity_id)

    def create(self, **data: object) -> ModelT:
        """Cria uma entidade e a sincroniza com a sessao atual."""

        try:
            entity = self.model(**data)
            self.session.add(entity)
            self.session.flush()
            return entity
        except SQLAlchemyError:
            LOGGER.exception("Falha ao criar entidade de %s", self.model.__name__)
            raise

    def add(self, **data: object) -> ModelT:
        """Alias retrocompativel para create."""

        return self.create(**data)

    def update(self, entity: ModelT, **data: object) -> ModelT:
        """Atualiza uma entidade existente."""

        try:
            for field, value in data.items():
                setattr(entity, field, value)
            self.session.add(entity)
            self.session.flush()
            return entity
        except SQLAlchemyError:
            LOGGER.exception("Falha ao atualizar entidade de %s", self.model.__name__)
            raise

    def delete(self, entity: ModelT) -> None:
        """Remove uma entidade existente."""

        try:
            self.session.delete(entity)
            self.session.flush()
        except SQLAlchemyError:
            LOGGER.exception("Falha ao remover entidade de %s", self.model.__name__)
            raise


class UnitOfWork:
    """Agrupa repositories sobre a mesma sessao transacional."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def repository(self, model: type[ModelT]) -> Repository[ModelT]:
        """Cria um repository tipado para o modelo informado."""

        return Repository(self.session, model)
