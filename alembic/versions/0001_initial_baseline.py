"""initial baseline

Revision ID: 0001_initial_baseline
Revises: 
Create Date: 2026-03-19 00:00:00
"""
from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001_initial_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Cria tabela de versao e baseline de migracao."""

    op.execute("SELECT 1")


def downgrade() -> None:
    """Downgrade baseline sem alteracoes estruturais."""

    op.execute("SELECT 1")
