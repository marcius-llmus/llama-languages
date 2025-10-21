from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.settings.repositories import SettingsRepository
from app.settings.services import SettingsPageService, SettingsService


def get_settings_repository(db: Session = Depends(get_db)) -> SettingsRepository:
    return SettingsRepository(db=db)


def get_settings_service(
    repository: SettingsRepository = Depends(get_settings_repository),
) -> SettingsService:
    return SettingsService(settings_repository=repository)


def get_settings_page_service(
    settings_service: SettingsService = Depends(get_settings_service),
) -> SettingsPageService:
    return SettingsPageService(settings_service=settings_service)
