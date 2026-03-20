"""phoenix 3 expansion

Revision ID: 0004_phoenix3_expansion
Revises: 0002_full_schema_ddl
Create Date: 2026-03-20 00:30:00
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0004_phoenix3_expansion"
down_revision = "0002_full_schema_ddl"
branch_labels = None
depends_on = None


def _table_columns(table_name: str) -> set[str]:
    rows = op.get_bind().execute(sa.text(f"PRAGMA table_info('{table_name}');")).fetchall()
    return {row[1] for row in rows}


def _table_exists(table_name: str) -> bool:
    rows = op.get_bind().execute(
        sa.text("SELECT name FROM sqlite_master WHERE type='table' AND name=:name"),
        {"name": table_name},
    ).fetchall()
    return bool(rows)


def _add_column_if_missing(table_name: str, column_name: str, ddl: str) -> None:
    if column_name not in _table_columns(table_name):
        op.execute(sa.text(f"ALTER TABLE {table_name} ADD COLUMN {ddl}"))


def upgrade() -> None:
    if not _table_exists("achievements"):
        op.create_table(
            "achievements",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("key", sa.String(length=80), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("icon", sa.String(length=16), nullable=False, server_default="*"),
            sa.Column("category", sa.String(length=40), nullable=False),
            sa.Column("xp_reward", sa.Integer(), nullable=False, server_default="10"),
            sa.Column("rarity", sa.String(length=20), nullable=False, server_default="common"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("key", name="uq_achievements_key"),
            sa.PrimaryKeyConstraint("id"),
            sqlite_autoincrement=True,
        )
    op.execute(sa.text("CREATE UNIQUE INDEX IF NOT EXISTS ix_achievement_key ON achievements (key)"))

    if not _table_exists("user_achievements"):
        op.create_table(
            "user_achievements",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("achievement_id", sa.Integer(), nullable=False),
            sa.Column("unlocked_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("progress", sa.Float(), nullable=False, server_default="1"),
            sa.Column("notified", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.ForeignKeyConstraint(["achievement_id"], ["achievements.id"]),
            sa.PrimaryKeyConstraint("id"),
            sqlite_autoincrement=True,
        )
    op.execute(sa.text("CREATE INDEX IF NOT EXISTS ix_user_achievement_aid ON user_achievements (achievement_id)"))

    if not _table_exists("ai_insights"):
        op.create_table(
            "ai_insights",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("type", sa.String(length=20), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("generated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.Column("dismissed", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.PrimaryKeyConstraint("id"),
            sqlite_autoincrement=True,
        )

    if not _table_exists("sprints"):
        op.create_table(
            "sprints",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=140), nullable=False),
            sa.Column("start_date", sa.Date(), nullable=True),
            sa.Column("end_date", sa.Date(), nullable=True),
            sa.Column("goal", sa.Text(), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=False, server_default="planned"),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
            sa.PrimaryKeyConstraint("id"),
            sqlite_autoincrement=True,
        )

    _add_column_if_missing("journal_entries", "word_count", "word_count INTEGER DEFAULT 0")
    _add_column_if_missing("journal_entries", "template", "template VARCHAR(50)")

    _add_column_if_missing("tasks", "start_date", "start_date DATE")
    _add_column_if_missing("tasks", "progress", "progress INTEGER DEFAULT 0")
    _add_column_if_missing("tasks", "sprint_id", "sprint_id INTEGER")
    _add_column_if_missing("tasks", "depends_on", "depends_on INTEGER")
    _add_column_if_missing("tasks", "time_logged", "time_logged INTEGER DEFAULT 0")


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS ai_insights"))
    op.execute(sa.text("DROP TABLE IF EXISTS user_achievements"))
    op.execute(sa.text("DROP TABLE IF EXISTS achievements"))
    op.execute(sa.text("DROP TABLE IF EXISTS sprints"))
