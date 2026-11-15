from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class DatabaseHealth(BaseModel):
    type: str = Field(..., description="Database engine type")
    status: str = Field(..., description="Current database status")
    database_path: str = Field(..., description="Resolved SQLite database path")
    message: str | None = Field(default=None, description="Optional database health message")


class HealthStatusResponse(BaseModel):
    status: Literal["ok", "degraded"] = Field(..., description="Overall application health")
    service: str = Field(..., description="Application/service name")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Runtime environment")
    timestamp: datetime = Field(..., description="UTC timestamp for the health report")
    database: DatabaseHealth = Field(..., description="Database health status")
    readiness: Literal["ready", "not_ready"] = Field(..., description="Readiness for serving requests")
