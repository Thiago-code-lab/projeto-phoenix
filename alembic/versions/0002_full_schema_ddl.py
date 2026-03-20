"""full schema DDL

Revision ID: 0002_full_schema_ddl
Revises: 0001_initial_baseline
Create Date: 2026-03-19 00:01:00
"""
from __future__ import annotations

from alembic import op

from phoenix.core.models import Base

# revision identifiers, used by Alembic.
revision = "0002_full_schema_ddl"
down_revision = "0001_initial_baseline"
branch_labels = None
depends_on = None

INDEX_STATEMENTS: list[str] = []

DROP_INDEX_STATEMENTS: list[str] = []

TABLE_DROP_ORDER = [
    "goal_milestones",
    "habit_logs",
    "transactions",
    "budgets",
    "accounts",
    "books",
    "health_logs",
    "workouts",
    "journal_entries",
    "focus_sessions",
    "tasks",
    "projects",
    "notes",
    "reviews",
    "habits",
    "goals",
    "user_profile",
]


def upgrade() -> None:
    """Cria todas as tabelas da aplicacao e indices essenciais."""

    bind = op.get_bind()
    Base.metadata.create_all(bind=bind, checkfirst=True)
    for statement in INDEX_STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    """Remove indices e tabelas em ordem segura de dependencias."""

    for statement in DROP_INDEX_STATEMENTS:
        op.execute(statement)

    for table_name in TABLE_DROP_ORDER:
        op.execute(f"DROP TABLE IF EXISTS {table_name}")
