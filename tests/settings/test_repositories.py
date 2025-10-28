from app.commons.enums import GeminiModel
from app.settings.models import LLMSettings, Settings
from app.settings.repositories import LLMSettingsRepository, SettingsRepository
from app.settings.schemas import LLMSettingsCreate, LLMSettingsUpdate, SettingsUpdate


class TestSettingsRepository:
    def test_get_settings(self, settings_repository: SettingsRepository, settings: Settings):
        retrieved_settings = settings_repository.get(pk=settings.id)
        assert retrieved_settings is not None
        assert retrieved_settings.id == settings.id

    def test_update_settings(
        self, settings_repository: SettingsRepository, settings: Settings
    ):
        update_data = SettingsUpdate(feedback_language="Spanish")
        updated_settings = settings_repository.update(db_obj=settings, obj_in=update_data)
        assert updated_settings.feedback_language == "Spanish"


class TestLLMSettingsRepository:
    def test_create_llm_settings(self, llm_settings_repository: LLMSettingsRepository):
        settings_in = LLMSettingsCreate(model=GeminiModel.GEMINI_2_5_FLASH, temperature=0.5)
        created_settings = llm_settings_repository.create(obj_in=settings_in)
        assert created_settings.id is not None
        assert created_settings.model == GeminiModel.GEMINI_2_5_FLASH

    def test_get_llm_settings(
        self, llm_settings_repository: LLMSettingsRepository, settings: Settings
    ):
        retrieved_settings = llm_settings_repository.get(pk=settings.transcription_settings_id)
        assert retrieved_settings is not None
        assert retrieved_settings.id == settings.transcription_settings_id

    def test_update_llm_settings(
        self, llm_settings_repository: LLMSettingsRepository, settings: Settings
    ):
        db_obj = llm_settings_repository.get(pk=settings.transcription_settings_id)
        update_data = LLMSettingsUpdate(
            model=GeminiModel.GEMINI_2_5_FLASH, temperature=0.9
        )
        updated_settings = llm_settings_repository.update(db_obj=db_obj, obj_in=update_data)
        assert updated_settings.temperature == 0.9