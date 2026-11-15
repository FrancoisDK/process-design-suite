from __future__ import annotations

import json
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
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS hydraulics_cases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    model TEXT NOT NULL,
                    inputs_json TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    warnings_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
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

    def list_hydraulics_cases(self) -> list[dict[str, Any]]:
        with self.get_connection() as connection:
            rows = connection.execute(
                """
                SELECT id, name, model, created_at
                FROM hydraulics_cases
                ORDER BY id DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def create_hydraulics_case(
        self,
        *,
        name: str,
        model: str,
        inputs: dict[str, Any],
        result: dict[str, Any],
        warnings: list[str],
    ) -> int:
        with self.get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO hydraulics_cases (name, model, inputs_json, result_json, warnings_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    name,
                    model,
                    json.dumps(inputs, separators=(",", ":")),
                    json.dumps(result, separators=(",", ":")),
                    json.dumps(warnings, separators=(",", ":")),
                ),
            )
            return int(cursor.lastrowid)

    def get_hydraulics_case(self, case_id: int) -> dict[str, Any] | None:
        with self.get_connection() as connection:
            row = connection.execute(
                """
                SELECT id, name, model, inputs_json, result_json, warnings_json, created_at
                FROM hydraulics_cases
                WHERE id = ?
                """,
                (case_id,),
            ).fetchone()
        if row is None:
            return None
        payload = dict(row)
        payload["inputs"] = json.loads(payload.pop("inputs_json"))
        payload["result"] = json.loads(payload.pop("result_json"))
        payload["warnings"] = json.loads(payload.pop("warnings_json"))
        return payload

    def delete_hydraulics_case(self, case_id: int) -> bool:
        with self.get_connection() as connection:
            cursor = connection.execute("DELETE FROM hydraulics_cases WHERE id = ?", (case_id,))
            return cursor.rowcount > 0

    def update_hydraulics_case_name(self, case_id: int, name: str) -> bool:
        with self.get_connection() as connection:
            cursor = connection.execute(
                "UPDATE hydraulics_cases SET name = ? WHERE id = ?",
                (name, case_id),
            )
            return cursor.rowcount > 0

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
