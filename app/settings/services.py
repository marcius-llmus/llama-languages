from app.commons.enums import GeminiModel
from app.settings.models import LLMSettings, Settings
from app.settings.repositories import LLMSettingsRepository, SettingsRepository
from app.settings.schemas import (
    LLMSettingsCreate,
    LLMSettingsUpdate,
    SettingsCreate,
    SettingsUpdate,
)


class SettingsService:
    def __init__(
        self,
        settings_repository: SettingsRepository,
        llm_settings_service: "LLMSettingsService",
    ):
        self.settings_repository = settings_repository
        self.llm_settings_service = llm_settings_service

    def get_settings(self) -> Settings:
        settings = self.settings_repository.get(pk=1)  # hard coded, local host only
        if not settings:
            transcription_settings = self.llm_settings_service.get_or_create(
                llm_settings_id=None,
                settings_in=LLMSettingsCreate(
                    model=GeminiModel.GEMINI_2_5_FLASH, temperature=0.0
                ),
            )
            persona_settings = self.llm_settings_service.get_or_create(
                llm_settings_id=None,
                settings_in=LLMSettingsCreate(
                    model=GeminiModel.GEMINI_2_5_PRO, temperature=0.7
                ),
            )
            feedback_settings = self.llm_settings_service.get_or_create(
                llm_settings_id=None,
                settings_in=LLMSettingsCreate(
                    model=GeminiModel.GEMINI_2_5_PRO, temperature=0.5
                ),
            )

            settings_in = SettingsCreate(
                transcription_settings_id=transcription_settings.id,
                persona_settings_id=persona_settings.id,
                feedback_settings_id=feedback_settings.id,
            )
            settings = self.settings_repository.create(obj_in=settings_in)
        return settings

    def update_settings(self, *, settings_in: SettingsUpdate) -> Settings:
        db_obj = self.get_settings()

        if settings_in.transcription_settings:
            self.llm_settings_service.update_llm_settings(
                llm_settings_id=db_obj.transcription_settings_id,
                settings_in=settings_in.transcription_settings,
            )

        if settings_in.persona_settings:
            self.llm_settings_service.update_llm_settings(
                llm_settings_id=db_obj.persona_settings_id,
                settings_in=settings_in.persona_settings,
            )

        if settings_in.feedback_settings:
            self.llm_settings_service.update_llm_settings(
                llm_settings_id=db_obj.feedback_settings_id,
                settings_in=settings_in.feedback_settings,
            )
        return self.settings_repository.update(db_obj=db_obj, obj_in=settings_in)

    def get_feedback_language(self) -> str:
        settings = self.get_settings()
        return settings.feedback_language or "English"


class LLMSettingsService:
    def __init__(self, llm_settings_repository: LLMSettingsRepository):
        self.llm_settings_repository = llm_settings_repository

    def get_llm_settings(self, llm_settings_id: int) -> LLMSettings | None:
        return self.llm_settings_repository.get(pk=llm_settings_id)

    def update_llm_settings(
        self, *, llm_settings_id: int, settings_in: LLMSettingsUpdate
    ) -> LLMSettings | None:
        """Fetches the LLMSettings object and applies the update."""
        db_obj = self.get_llm_settings(llm_settings_id)
        if not db_obj:
            return None
        return self.llm_settings_repository.update(db_obj=db_obj, obj_in=settings_in)

    def get_or_create(
        self, *, llm_settings_id: int | None, settings_in: LLMSettingsCreate
    ) -> LLMSettings:
        """
        Gets an LLMSettings object by its ID. If the ID is None or not found,
        it creates a new one using the provided schema.
        """
        if llm_settings_id is not None:
            db_obj = self.get_llm_settings(llm_settings_id)
            if db_obj:
                return db_obj

        # If no object was found or no ID was provided, create one.
        return self.llm_settings_repository.create(obj_in=settings_in)


class SettingsPageService:
    def __init__(self, settings_service: SettingsService):
        self.settings_service = settings_service

    def get_settings_page_data(self) -> dict:
        return {
            "settings": self.settings_service.get_settings(),
            "GeminiModel": GeminiModel,
        }