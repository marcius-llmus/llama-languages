import pytest
from unittest.mock import MagicMock

from app.commons.enums import GeminiModel
from app.settings.models import Settings
from app.settings.schemas import LLMSettingsUpdate, SettingsUpdate
from app.settings.services import LLMSettingsService, SettingsPageService, SettingsService


class TestSettingsService:
    def test_get_settings_raises_error_if_not_exist(
        self,
        settings_service: SettingsService,
        settings_repository_mock: MagicMock,
    ):
        settings_repository_mock.get.return_value = None

        with pytest.raises(RuntimeError, match="Settings not initialized"):
            settings_service.get_settings()

        settings_repository_mock.get.assert_called_once_with(pk=1)

    def test_get_settings_returns_existing(
        self,
        settings_service: SettingsService,
        settings: Settings,
        settings_repository_mock: MagicMock,
    ):
        settings_repository_mock.get.return_value = settings

        result = settings_service.get_settings()

        settings_repository_mock.get.assert_called_once_with(pk=1)
        assert result == settings

    def test_update_settings(
        self,
        settings_service: SettingsService,
        settings: Settings,
        settings_repository_mock: MagicMock,
        llm_settings_service_mock: MagicMock,
    ):
        settings_repository_mock.get.return_value = settings
        update_in = SettingsUpdate(
            feedback_language="French",
            persona_settings=LLMSettingsUpdate(
                model=GeminiModel.GEMINI_2_5_PRO, temperature=0.9
            ),
        )

        settings_service.update_settings(settings_in=update_in)

        llm_settings_service_mock.update_llm_settings.assert_called_once_with(
            llm_settings_id=settings.persona_settings_id,
            settings_in=update_in.persona_settings,
        )
        settings_repository_mock.update.assert_called_once_with(
            db_obj=settings, obj_in=update_in
        )

    def test_get_feedback_language(
        self,
        settings_service: SettingsService,
        settings: Settings,
        settings_repository_mock: MagicMock,
    ):
        settings.feedback_language = "Spanish"
        settings_repository_mock.get.return_value = settings
        assert settings_service.get_feedback_language() == "Spanish"


class TestLLMSettingsService:
    def test_get_llm_settings(self, llm_settings_service: LLMSettingsService, llm_settings_repository_mock: MagicMock):
        llm_settings_service.get_llm_settings(llm_settings_id=1)
        llm_settings_repository_mock.get.assert_called_once_with(pk=1)

    def test_update_llm_settings(
        self, llm_settings_service: LLMSettingsService, llm_settings_repository_mock: MagicMock, settings: Settings
    ):
        llm_settings_repository_mock.get.return_value = settings.persona_settings
        update_in = LLMSettingsUpdate(
            model=GeminiModel.GEMINI_2_5_FLASH, temperature=0.8
        )

        llm_settings_service.update_llm_settings(
            llm_settings_id=settings.persona_settings_id, settings_in=update_in
        )

        llm_settings_repository_mock.get.assert_called_once_with(settings.persona_settings_id)
        llm_settings_repository_mock.update.assert_called_once_with(
            db_obj=settings.persona_settings, obj_in=update_in
        )

    def test_get_or_create(self, llm_settings_service: LLMSettingsService, llm_settings_repository_mock: MagicMock, settings: Settings):

        # Case 1: ID provided and found
        llm_settings_repository_mock.get.return_value = settings.persona_settings
        llm_settings_service.get_or_create(llm_settings_id=settings.persona_settings_id, settings_in=MagicMock())
        llm_settings_repository_mock.get.assert_called_once_with(settings.persona_settings_id)
        llm_settings_repository_mock.create.assert_not_called()

        # Case 2: ID is None, should create
        llm_settings_repository_mock.reset_mock()
        settings_in = MagicMock()
        llm_settings_service.get_or_create(llm_settings_id=None, settings_in=settings_in)
        llm_settings_repository_mock.get.assert_not_called()
        llm_settings_repository_mock.create.assert_called_once_with(obj_in=settings_in)


class TestSettingsPageService:
    def test_get_settings_page_data(
        self,
        settings_page_service: SettingsPageService,
        settings_service_mock: MagicMock,
        settings: Settings,
    ):
        settings_service_mock.get_settings.return_value = settings
        result = settings_page_service.get_settings_page_data()
        settings_service_mock.get_settings.assert_called_once()
        assert result["settings"] == settings
        assert result["GeminiModel"] == GeminiModel