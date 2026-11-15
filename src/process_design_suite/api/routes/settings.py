from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from process_design_suite.schemas.settings import UpdateUserPreferences, UserPreferences
from process_design_suite.services.settings_service import SettingsService

router = APIRouter(tags=["settings"])


def get_settings_service(request: Request) -> SettingsService:
    database = getattr(request.app.state, "database", None)
    return SettingsService(database=database)


@router.get("/settings/preferences", response_model=UserPreferences)
async def get_user_preferences(service: SettingsService = Depends(get_settings_service)) -> UserPreferences:
    return service.get_user_preferences()


@router.put("/settings/preferences", response_model=UserPreferences)
async def update_user_preferences(
    payload: UpdateUserPreferences, service: SettingsService = Depends(get_settings_service)
) -> UserPreferences:
    return service.update_user_preferences(payload)
