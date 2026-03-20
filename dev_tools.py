from __future__ import annotations

"""Ferramentas de desenvolvimento para o Phoenix.

Uso:
    python dev_tools.py reset_db
    python dev_tools.py seed_demo_data
    python dev_tools.py run_migrations
    python dev_tools.py check_health
    python dev_tools.py build_native
    python dev_tools.py check_warnings
    python dev_tools.py profile_app
    python dev_tools.py run_web_server
"""

import argparse
import cProfile
import pstats
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path

from phoenix.core.database import DATABASE_PATH, SessionLocal, init_database, run_integrity_check
from phoenix.core.models import FocusSession, Goal, Habit, Transaction
from phoenix.web.server import run_server


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


def build_native() -> None:
    """Compila extensao Rust com maturin quando disponivel."""

    native_dir = Path(__file__).resolve().parent / "phoenix_native"
    if not native_dir.exists():
        print("phoenix_native nao encontrado. Pule esta etapa por enquanto.")
        return
    try:
        subprocess.run(["maturin", "develop", "--release"], cwd=str(native_dir), check=True)
        print("Extensao nativa compilada com sucesso.")
    except Exception as exc:  # noqa: BLE001
        print(f"Aviso: falha ao compilar extensao nativa ({exc}). Fallback Python permanece ativo.")


def check_warnings() -> None:
    """Executa bootstrap do app tratando warnings como erro."""

    subprocess.run(["python", "-W", "error", "-m", "phoenix.main"], check=False)


def profile_app() -> None:
    """Roda perfil simplificado de operacoes criticas e mostra top 10."""

    profiler = cProfile.Profile()
    profiler.enable()

    init_database()
    session = SessionLocal()
    try:
        session.query(Goal).count()
        session.query(Habit).count()
        session.query(Transaction).count()
        session.query(FocusSession).count()
    finally:
        session.close()

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("cumulative")
    stats.print_stats(10)


def run_web_server() -> None:
    """Sobe API local (FastAPI quando disponivel, senão stdlib)."""

    run_server(host="127.0.0.1", port=8765)


def main() -> None:
    """Ponto de entrada para comandos utilitarios de desenvolvimento."""

    parser = argparse.ArgumentParser(description="Dev tools do Phoenix")
    parser.add_argument(
        "command",
        choices=[
            "reset_db",
            "seed_demo_data",
            "run_migrations",
            "check_health",
            "build_native",
            "check_warnings",
            "profile_app",
            "run_web_server",
        ],
        help="Comando a executar",
    )
    args = parser.parse_args()

    commands = {
        "reset_db": reset_db,
        "seed_demo_data": seed_demo_data,
        "run_migrations": run_migrations,
        "check_health": check_health,
        "build_native": build_native,
        "check_warnings": check_warnings,
        "profile_app": profile_app,
        "run_web_server": run_web_server,
    }
    commands[args.command]()


if __name__ == "__main__":
    main()
