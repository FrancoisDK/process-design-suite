from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "process-design-suite"
    app_version: str = "0.1.0"
    environment: str = "development"
    database_path: str = "process_design_suite.db"

    @property
    def database_file(self) -> Path:
        root_dir = Path(__file__).resolve().parents[2]
        return (root_dir / self.database_path).resolve()


def get_settings() -> Settings:
    return Settings()
