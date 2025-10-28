from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture
from sqlmodel import Session

from app.main import app
from app.personas.dependencies import get_persona_repository, get_persona_service, get_persona_page_service
from app.personas.models import Persona
from app.personas.repositories import PersonaRepository
from app.personas.services import PersonaPageService, PersonaService


@pytest.fixture
def persona_repository(db_session: Session) -> PersonaRepository:
    return PersonaRepository(db=db_session)


@pytest.fixture
def persona(db_session: Session) -> Persona:
    db_persona = Persona(name="Test Persona", prompt="A persona for testing.")
    db_session.add(db_persona)
    db_session.flush()
    return db_persona


@pytest.fixture
def persona_repository_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(PersonaRepository, instance=True)


@pytest.fixture
def persona_service(persona_repository_mock: MagicMock) -> PersonaService:
    """Provides a real PersonaService instance with a mocked repository for unit testing."""
    return PersonaService(persona_repository=persona_repository_mock)


@pytest.fixture
def persona_service_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(PersonaService, instance=True)


@pytest.fixture
def persona_page_service(persona_service_mock: MagicMock) -> PersonaPageService:
    """Provides a real PersonaPageService instance with a mocked persona_service."""
    return PersonaPageService(persona_service=persona_service_mock)


@pytest.fixture
def persona_page_service_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(PersonaPageService, instance=True)


@pytest.fixture
def override_get_persona_service(persona_service_mock: MagicMock):
    """
    This fixture is useful for testing routes, as it replaces the real service
    with a mock, isolating the route logic.
    """
    app.dependency_overrides[get_persona_service] = lambda: persona_service_mock
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def override_get_persona_page_service(persona_page_service_mock: MagicMock):
    app.dependency_overrides[get_persona_page_service] = lambda: persona_page_service_mock
    yield
    app.dependency_overrides.clear()
