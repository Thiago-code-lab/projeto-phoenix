from __future__ import annotations

"""Ferramentas de desenvolvimento para o Phoenix.

Uso:
    python dev_tools.py reset_db
    python dev_tools.py seed_demo_data
    python dev_tools.py run_migrations
    python dev_tools.py check_health
"""

import argparse
import subprocess
from datetime import date, datetime, timedelta

from phoenix.core.database import DATABASE_PATH, SessionLocal, init_database, run_integrity_check
from phoenix.core.models import FocusSession, Goal, Habit, Transaction


def reset_db() -> None:
    """Remove o banco local atual e recria o schema."""

    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
    init_database()
    print("Banco resetado com sucesso.")


def seed_demo_data() -> None:
    """Insere dados demonstrativos usando operacoes em lote."""

    init_database()
    session = SessionLocal()
    try:
        today = date.today()
        session.bulk_insert_mappings(
            Goal,
            [
                {"title": "Estudar AWS", "category": "carreira", "status": "active", "target_value": 80, "current_value": 20, "target_date": today + timedelta(days=45)},
                {"title": "Ler 12 livros", "category": "aprendizado", "status": "active", "target_value": 12, "current_value": 3, "target_date": today + timedelta(days=200)},
            ],
        )
        session.bulk_insert_mappings(
            Habit,
            [
                {"name": "Leitura diaria", "frequency": "daily", "active": True},
                {"name": "Treino funcional", "frequency": "daily", "active": True},
            ],
        )
        session.bulk_insert_mappings(
            Transaction,
            [
                {"title": "Salario", "amount": 6500.0, "type": "income", "category": "Salario", "account": "Principal", "date": today.replace(day=1)},
                {"title": "Aluguel", "amount": 1800.0, "type": "expense", "category": "Moradia", "account": "Principal", "date": today.replace(day=3)},
                {"title": "Mercado", "amount": 620.5, "type": "expense", "category": "Alimentacao", "account": "Principal", "date": today.replace(day=6)},
            ],
        )
        session.bulk_insert_mappings(
            FocusSession,
            [
                {"date": today - timedelta(days=1), "start_time": datetime.now() - timedelta(days=1), "duration_min": 25, "completed": True},
                {"date": today, "start_time": datetime.now(), "duration_min": 50, "completed": True},
            ],
        )
        session.commit()
        print("Dados demo inseridos.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def run_migrations() -> None:
    """Executa migracoes Alembic ate a revisao mais recente."""

    subprocess.run(["alembic", "upgrade", "head"], check=True)
    print("Migracoes executadas.")


def check_health() -> None:
    """Roda health check de integridade do SQLite."""

    run_integrity_check()
    print("Banco integro (PRAGMA integrity_check = ok).")


def main() -> None:
    """Ponto de entrada para comandos utilitarios de desenvolvimento."""

    parser = argparse.ArgumentParser(description="Dev tools do Phoenix")
    parser.add_argument(
        "command",
        choices=["reset_db", "seed_demo_data", "run_migrations", "check_health"],
        help="Comando a executar",
    )
    args = parser.parse_args()

    commands = {
        "reset_db": reset_db,
        "seed_demo_data": seed_demo_data,
        "run_migrations": run_migrations,
        "check_health": check_health,
    }
    commands[args.command]()


if __name__ == "__main__":
    main()
