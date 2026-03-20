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

INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS ix_goals_status ON goals (status)",
    "CREATE INDEX IF NOT EXISTS ix_goals_target_date ON goals (target_date)",
    "CREATE INDEX IF NOT EXISTS ix_goal_milestones_goal_id ON goal_milestones (goal_id)",
    "CREATE INDEX IF NOT EXISTS ix_habits_active ON habits (active)",
    "CREATE INDEX IF NOT EXISTS ix_habit_logs_habit_id ON habit_logs (habit_id)",
    "CREATE INDEX IF NOT EXISTS ix_habit_logs_date ON habit_logs (date)",
    "CREATE INDEX IF NOT EXISTS ix_transactions_date ON transactions (date)",
    "CREATE INDEX IF NOT EXISTS ix_transactions_type ON transactions (type)",
    "CREATE INDEX IF NOT EXISTS ix_transactions_category ON transactions (category)",
    "CREATE INDEX IF NOT EXISTS ix_budgets_category ON budgets (category)",
    "CREATE INDEX IF NOT EXISTS ix_books_status ON books (status)",
    "CREATE INDEX IF NOT EXISTS ix_books_updated_at ON books (updated_at)",
    "CREATE INDEX IF NOT EXISTS ix_health_logs_date ON health_logs (date)",
    "CREATE INDEX IF NOT EXISTS ix_workouts_date ON workouts (date)",
    "CREATE INDEX IF NOT EXISTS ix_journal_entries_date ON journal_entries (date)",
    "CREATE INDEX IF NOT EXISTS ix_projects_active ON projects (active)",
    "CREATE INDEX IF NOT EXISTS ix_tasks_project_id ON tasks (project_id)",
    "CREATE INDEX IF NOT EXISTS ix_tasks_status ON tasks (status)",
    "CREATE INDEX IF NOT EXISTS ix_tasks_due_date ON tasks (due_date)",
    "CREATE INDEX IF NOT EXISTS ix_focus_sessions_date ON focus_sessions (date)",
    "CREATE INDEX IF NOT EXISTS ix_focus_sessions_task_id ON focus_sessions (task_id)",
    "CREATE INDEX IF NOT EXISTS ix_notes_parent_id ON notes (parent_id)",
    "CREATE INDEX IF NOT EXISTS ix_notes_updated_at ON notes (updated_at)",
    "CREATE INDEX IF NOT EXISTS ix_reviews_period_type ON reviews (period_type)",
    "CREATE INDEX IF NOT EXISTS ix_reviews_created_at ON reviews (created_at)",
]

DROP_INDEX_STATEMENTS = [
    "DROP INDEX IF EXISTS ix_reviews_created_at",
    "DROP INDEX IF EXISTS ix_reviews_period_type",
    "DROP INDEX IF EXISTS ix_notes_updated_at",
    "DROP INDEX IF EXISTS ix_notes_parent_id",
    "DROP INDEX IF EXISTS ix_focus_sessions_task_id",
    "DROP INDEX IF EXISTS ix_focus_sessions_date",
    "DROP INDEX IF EXISTS ix_tasks_due_date",
    "DROP INDEX IF EXISTS ix_tasks_status",
    "DROP INDEX IF EXISTS ix_tasks_project_id",
    "DROP INDEX IF EXISTS ix_projects_active",
    "DROP INDEX IF EXISTS ix_journal_entries_date",
    "DROP INDEX IF EXISTS ix_workouts_date",
    "DROP INDEX IF EXISTS ix_health_logs_date",
    "DROP INDEX IF EXISTS ix_books_updated_at",
    "DROP INDEX IF EXISTS ix_books_status",
    "DROP INDEX IF EXISTS ix_budgets_category",
    "DROP INDEX IF EXISTS ix_transactions_category",
    "DROP INDEX IF EXISTS ix_transactions_type",
    "DROP INDEX IF EXISTS ix_transactions_date",
    "DROP INDEX IF EXISTS ix_habit_logs_date",
    "DROP INDEX IF EXISTS ix_habit_logs_habit_id",
    "DROP INDEX IF EXISTS ix_habits_active",
    "DROP INDEX IF EXISTS ix_goal_milestones_goal_id",
    "DROP INDEX IF EXISTS ix_goals_target_date",
    "DROP INDEX IF EXISTS ix_goals_status",
]

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
