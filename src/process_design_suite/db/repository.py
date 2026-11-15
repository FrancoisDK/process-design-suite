from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


class DatabaseRepository:
    def __init__(self, database_path: str | Path | None = None) -> None:
        if database_path is None:
            root_dir = Path(__file__).resolve().parents[2]
            database_path = root_dir / "process_design_suite.db"

        self.database_path = Path(database_path).resolve()
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.database_path))
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.get_connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS application_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            connection.execute(
                "INSERT OR IGNORE INTO application_state (key, value) VALUES (?, ?)",
                ("app_name", "process-design-suite"),
            )
            connection.execute(
                "INSERT OR IGNORE INTO application_state (key, value) VALUES (?, ?)",
                ("database_status", "ready"),
            )
            connection.execute(
                "INSERT OR IGNORE INTO application_state (key, value) VALUES (?, ?)",
                ("length_unit", "mm"),
            )
            connection.execute(
                "INSERT OR IGNORE INTO application_state (key, value) VALUES (?, ?)",
                ("decimal_precision", "3"),
            )
            connection.execute(
                "INSERT OR IGNORE INTO application_state (key, value) VALUES (?, ?)",
                ("pressure_unit", "kPa"),
            )
            connection.execute(
                "INSERT OR IGNORE INTO application_state (key, value) VALUES (?, ?)",
                ("pressure_profile", "sea-level"),
            )
            connection.execute(
                "INSERT OR IGNORE INTO application_state (key, value) VALUES (?, ?)",
                ("atmospheric_pressure_kpa", "101.325"),
            )

    def get_application_state(self, key: str) -> str | None:
        with self.get_connection() as connection:
            row = connection.execute("SELECT value FROM application_state WHERE key = ?", (key,)).fetchone()
        return str(row["value"]) if row is not None else None

    def set_application_state(self, key: str, value: str) -> None:
        with self.get_connection() as connection:
            connection.execute(
                """
                INSERT INTO application_state (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                  value = excluded.value,
                  updated_at = CURRENT_TIMESTAMP
                """,
                (key, value),
            )

    def health_check(self) -> dict[str, Any]:
        try:
            with self.get_connection() as connection:
                connection.execute("SELECT 1").fetchone()
            return {
                "type": "sqlite",
                "status": "ready",
                "database_path": str(self.database_path),
            }
        except sqlite3.DatabaseError as exc:
            return {
                "type": "sqlite",
                "status": "error",
                "database_path": str(self.database_path),
                "message": str(exc),
            }
