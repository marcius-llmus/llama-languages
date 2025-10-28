from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from app.main import app
from app.conversation.services import ConversationService
from app.conversation.workflows import ConversationWorkflow
from app.conversation.dependencies import get_conversation_service


@pytest.fixture
def conversation_workflow_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(ConversationWorkflow, instance=True)


@pytest.fixture
def conversation_service(conversation_workflow_mock: MagicMock) -> ConversationService:
    """Provides a real ConversationService instance but with a mocked workflow."""
    return ConversationService(workflow=conversation_workflow_mock)


@pytest.fixture
def conversation_service_mock(mocker: MockerFixture) -> MagicMock:
    return mocker.create_autospec(ConversationService, instance=True)


@pytest.fixture
def override_get_conversation_service(conversation_service_mock: MagicMock):
    app.dependency_overrides[get_conversation_service] = lambda: conversation_service_mock
    yield
    app.dependency_overrides.clear()
