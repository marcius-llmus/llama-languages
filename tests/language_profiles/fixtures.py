from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlmodel import Session

from app.main import app
from app.language_profiles.dependencies import (
    get_language_profile_page_service,
    get_language_profile_service,
)
from app.language_profiles.models import LanguageProfile, PracticeTopic
from app.language_profiles.repositories import (
    LanguageProfileRepository,
    PracticeTopicRepository,
)
from app.language_profiles.services import LanguageProfilePageService, LanguageProfileService
from app.personas.models import Persona
from tests.personas.fixtures import persona  # noqa F401


@pytest.fixture
def language_profile_repository(db_session: Session) -> LanguageProfileRepository:
    return LanguageProfileRepository(db=db_session)


@pytest.fixture
def practice_topic_repository(db_session: Session) -> PracticeTopicRepository:
    return PracticeTopicRepository(db=db_session)


@pytest.fixture
def language_profile(db_session: Session, persona: Persona) -> LanguageProfile:
    db_profile = LanguageProfile(
        name="Test Profile", target_language="Spanish", persona_id=persona.id
    )
    db_session.add(db_profile)
    db_session.flush()
    return db_profile


@pytest.fixture
def practice_topic(
    db_session: Session,
    language_profile: LanguageProfile,
) -> PracticeTopic:
    db_topic = PracticeTopic(name="Ordering Coffee", language_profile_id=language_profile.id)
    db_session.add(db_topic)
    db_session.flush()
    return db_topic


@pytest.fixture
def language_profile_repository_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(LanguageProfileRepository, instance=True)


@pytest.fixture
def practice_topic_repository_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(PracticeTopicRepository, instance=True)


@pytest.fixture
def language_profile_service(
    language_profile_repository_mock: MagicMock,
    practice_topic_repository_mock: MagicMock,
) -> LanguageProfileService:
    """Provides a real LanguageProfileService instance with mocked repositories for unit testing."""
    return LanguageProfileService(
        language_profile_repository=language_profile_repository_mock,
        practice_topic_repository=practice_topic_repository_mock,
    )


@pytest.fixture
def language_profile_service_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(LanguageProfileService, instance=True)


@pytest.fixture
def language_profile_page_service(
    language_profile_service_mock: MagicMock,
    persona_service_mock: MagicMock,
) -> LanguageProfilePageService:
    """Provides a real LanguageProfilePageService instance with mocked services."""
    return LanguageProfilePageService(
        language_profile_service=language_profile_service_mock,
        persona_service=persona_service_mock,
    )


@pytest.fixture
def language_profile_page_service_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(LanguageProfilePageService, instance=True)


@pytest.fixture
def override_get_language_profile_service(language_profile_service_mock: MagicMock):
    app.dependency_overrides[get_language_profile_service] = lambda: language_profile_service_mock
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def override_get_language_profile_page_service(
    language_profile_page_service_mock: MagicMock,
):
    app.dependency_overrides[get_language_profile_page_service] = lambda: language_profile_page_service_mock
    yield
    app.dependency_overrides.clear()