from app.settings.models import Settings
from app.settings.repositories import SettingsRepository
from app.settings.schemas import SettingsUpdate


class SettingsService:
    def __init__(self, settings_repository: SettingsRepository):
        self.settings_repository = settings_repository

    def get_settings(self) -> Settings:
        settings = self.settings_repository.get(pk=1) # hard coded, local host only
        if not settings:
            settings = self.settings_repository.create(obj_in=SettingsUpdate())
        return settings

    def update_settings(self, *, settings_in: SettingsUpdate) -> Settings:
        db_obj = self.get_settings()
        return self.settings_repository.update(db_obj=db_obj, obj_in=settings_in)


class SettingsPageService:
    def __init__(self, settings_service: SettingsService):
        self.settings_service = settings_service

    def get_settings_page_data(self) -> dict:
        return {"settings": self.settings_service.get_settings()}
