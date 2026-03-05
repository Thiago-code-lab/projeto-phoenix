from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import Any

from config import DB_PATH, DEFAULT_SETTINGS


class Database:
    def __init__(self, db_path: str = str(DB_PATH)) -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def query(self, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [dict(row) for row in rows]

    def query_one(self, sql: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(sql, params).fetchone()
            return dict(row) if row else None

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> int:
        with self._connect() as conn:
            cursor = conn.execute(sql, params)
            conn.commit()
            return cursor.lastrowid

    def execute_many(self, sql: str, params_list: list[tuple[Any, ...]]) -> None:
        with self._connect() as conn:
            conn.executemany(sql, params_list)
            conn.commit()


def init_db() -> None:
    db = Database()

    schema_statements = [
        """
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            target_value REAL,
            current_value REAL DEFAULT 0,
            unit TEXT,
            deadline DATE,
            status TEXT DEFAULT 'active',
            parent_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP,
            FOREIGN KEY (parent_id) REFERENCES goals(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            icon TEXT,
            description TEXT,
            frequency TEXT DEFAULT 'daily',
            target_count INTEGER DEFAULT 1,
            is_negative BOOLEAN DEFAULT 0,
            color TEXT,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS habit_logs (
            id INTEGER PRIMARY KEY,
            habit_id INTEGER NOT NULL,
            log_date DATE NOT NULL,
            count INTEGER DEFAULT 1,
            note TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS finance_categories (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT,
            icon TEXT,
            color TEXT,
            budget_limit REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category_id INTEGER,
            description TEXT,
            date DATE NOT NULL,
            recurrence TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP,
            FOREIGN KEY (category_id) REFERENCES finance_categories(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT,
            cover TEXT,
            total_pages INTEGER,
            pages_read INTEGER DEFAULT 0,
            genre TEXT,
            rating REAL,
            status TEXT DEFAULT 'quero_ler',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS reading_sessions (
            id INTEGER PRIMARY KEY,
            book_id INTEGER NOT NULL,
            session_date DATE NOT NULL,
            pages INTEGER DEFAULT 0,
            minutes INTEGER DEFAULT 0,
            quote TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES books(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY,
            workout_date DATE NOT NULL,
            exercise TEXT NOT NULL,
            sets INTEGER,
            reps INTEGER,
            weight REAL,
            duration_minutes INTEGER,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS body_metrics (
            id INTEGER PRIMARY KEY,
            metric_date DATE NOT NULL,
            weight REAL,
            body_fat REAL,
            waist REAL,
            chest REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS hydration_logs (
            id INTEGER PRIMARY KEY,
            log_date DATE NOT NULL,
            cups INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS sleep_logs (
            id INTEGER PRIMARY KEY,
            log_date DATE NOT NULL,
            hours REAL,
            quality INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS journal_entries (
            id INTEGER PRIMARY KEY,
            entry_date DATE NOT NULL,
            title TEXT,
            content TEXT NOT NULL,
            mood INTEGER,
            gratitude_1 TEXT,
            gratitude_2 TEXT,
            gratitude_3 TEXT,
            tags TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            color TEXT,
            description TEXT,
            deadline DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS project_columns (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            position INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS project_tasks (
            id INTEGER PRIMARY KEY,
            project_id INTEGER NOT NULL,
            column_id INTEGER NOT NULL,
            goal_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT,
            due_date DATE,
            labels TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id),
            FOREIGN KEY (column_id) REFERENCES project_columns(id),
            FOREIGN KEY (goal_id) REFERENCES goals(id)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP,
            deleted_at TIMESTAMP
        );
        """,
    ]

    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_goals_status ON goals(status);",
        "CREATE INDEX IF NOT EXISTS idx_goals_deadline ON goals(deadline);",
        "CREATE INDEX IF NOT EXISTS idx_habit_logs_date ON habit_logs(log_date);",
        "CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(date);",
        "CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(type);",
        "CREATE INDEX IF NOT EXISTS idx_journal_date ON journal_entries(entry_date);",
        "CREATE INDEX IF NOT EXISTS idx_project_tasks_due ON project_tasks(due_date);",
    ]

    for statement in schema_statements:
        db.execute(statement)
    for index_sql in indexes:
        db.execute(index_sql)

    for key, value in DEFAULT_SETTINGS.items():
        db.execute(
            """
            INSERT INTO app_settings(key, value, updated_at)
            VALUES(?, ?, ?)
            ON CONFLICT(key) DO NOTHING
            """,
            (key, value, datetime.now().isoformat()),
        )


def get_setting(key: str, default: str = "") -> str:
    db = Database()
    row = db.query_one("SELECT value FROM app_settings WHERE key = ? AND deleted_at IS NULL", (key,))
    return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    db = Database()
    db.execute(
        """
        INSERT INTO app_settings(key, value, updated_at)
        VALUES (?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET
          value = excluded.value,
          updated_at = excluded.updated_at,
          deleted_at = NULL
        """,
        (key, value, datetime.now().isoformat()),
    )


def soft_delete(table: str, row_id: int) -> None:
    db = Database()
    db.execute(
        f"UPDATE {table} SET deleted_at = ?, updated_at = ? WHERE id = ?",
        (datetime.now().isoformat(), datetime.now().isoformat(), row_id),
    )
