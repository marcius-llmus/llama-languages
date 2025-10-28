from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlmodel import Session

from app.main import app
from app.settings.dependencies import get_settings_page_service, get_settings_service
from app.commons.enums import GeminiModel
from app.settings.models import LLMSettings, Settings
from app.settings.repositories import LLMSettingsRepository, SettingsRepository
from app.settings.services import (
    LLMSettingsService,
    SettingsPageService,
    SettingsService,
)


@pytest.fixture
def llm_settings_repository(db_session: Session) -> LLMSettingsRepository:
    return LLMSettingsRepository(db=db_session)


@pytest.fixture
def settings_repository(db_session: Session) -> SettingsRepository:
    return SettingsRepository(db=db_session)


@pytest.fixture
def settings(
    db_session: Session,
) -> Settings:
    transcription_settings = LLMSettings(
        model=GeminiModel.GEMINI_2_5_FLASH, temperature=0.0
    )
    persona_settings = LLMSettings(model=GeminiModel.GEMINI_2_5_PRO, temperature=0.7)
    feedback_settings = LLMSettings(model=GeminiModel.GEMINI_2_5_PRO, temperature=0.5)
    db_session.add_all([transcription_settings, persona_settings, feedback_settings])
    db_session.flush()

    db_settings = Settings(
        id=1,
        transcription_settings_id=transcription_settings.id,
        persona_settings_id=persona_settings.id,
        feedback_settings_id=feedback_settings.id,
    )
    db_session.add(db_settings)
    db_session.flush()
    db_session.refresh(db_settings)
    return db_settings


@pytest.fixture
def llm_settings_repository_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(LLMSettingsRepository, instance=True)


@pytest.fixture
def settings_repository_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(SettingsRepository, instance=True)


@pytest.fixture
def llm_settings_service_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(LLMSettingsService, instance=True)


@pytest.fixture
def llm_settings_service(
    llm_settings_repository_mock: MagicMock,
) -> LLMSettingsService:
    """Provides a real LLMSettingsService instance with a mocked repository for unit testing."""
    return LLMSettingsService(llm_settings_repository=llm_settings_repository_mock)


@pytest.fixture
def settings_service(
    settings_repository_mock: MagicMock,
    llm_settings_service_mock: MagicMock,
    persona_service_mock: MagicMock,
    language_profile_service_mock: MagicMock,
) -> SettingsService:
    """
    Provides a real SettingsService instance with mocked dependencies (other services
    and repositories) for unit testing.
    """
    return SettingsService(
        settings_repository=settings_repository_mock,
        llm_settings_service=llm_settings_service_mock,
        persona_service=persona_service_mock,
        language_profile_service=language_profile_service_mock,
    )


@pytest.fixture
def settings_page_service(settings_service_mock: MagicMock) -> SettingsPageService:
    """Provides a real SettingsPageService instance with a mocked settings_service."""
    return SettingsPageService(settings_service=settings_service_mock)


@pytest.fixture
def settings_service_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(SettingsService, instance=True)


@pytest.fixture
def settings_page_service_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(SettingsPageService, instance=True)


@pytest.fixture
def override_get_settings_service(settings_service_mock: MagicMock):
    app.dependency_overrides[get_settings_service] = lambda: settings_service_mock
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def override_get_settings_page_service(settings_page_service_mock: MagicMock):
    app.dependency_overrides[
        get_settings_page_service
    ] = lambda: settings_page_service_mock
    yield
    app.dependency_overrides.clear()