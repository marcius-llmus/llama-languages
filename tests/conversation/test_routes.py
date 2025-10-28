from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.conversation.enums import ConversationEventType
from app.language_profiles.models import LanguageProfile
from app.personas.models import Persona


class TestConversationRoutes:
    def test_view_conversation_page(
        self,
        client: TestClient,
        language_profile_service_mock: MagicMock,
        override_get_language_profile_service,
    ):
        # Arrange: Mock the service to return a valid language profile with its persona
        mock_persona = Persona(id=1, name="Test Persona", prompt="p")
        language_profile_service_mock.get_language_profile.return_value = LanguageProfile(
            id=1,
            name="Test Profile",
            target_language="Klingon",
            persona_id=1,
            persona=mock_persona,
            practice_topics=[],  # This is required by the template
        )

        # Act
        response = client.get("/conversation/1")

        # Assert
        assert response.status_code == 200
        assert "Test Persona" in response.text
        assert "Klingon" in response.text
        language_profile_service_mock.get_language_profile.assert_called_once_with(1)

    def test_view_conversation_page_not_found(
        self,
        client: TestClient,
        language_profile_service_mock: MagicMock,
        override_get_language_profile_service,
    ):
        # Arrange: Mock the service to return None
        language_profile_service_mock.get_language_profile.return_value = None

        # Act
        response = client.get("/conversation/1")

        # Assert
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_conversation_websocket(
        self,
        client: TestClient,
        conversation_service_mock: MagicMock,
        override_get_conversation_service,
    ):
        # 1. Arrange
        language_profile_id = 1

        # Mock the async generator returned by the service
        async def mock_event_stream(*args, **kwargs):
            yield {"type": ConversationEventType.USER_TRANSCRIPTION_CHUNK_GENERATED, "data": "Hello"}
            yield {"type": ConversationEventType.AI_TEXT_CHUNK_GENERATED, "data": "Hi there!"}


        conversation_service_mock.run_conversation_turn = MagicMock(return_value=mock_event_stream())

        # 2. Act & Assert
        with client.websocket_connect(f"/conversation/ws/{language_profile_id}") as websocket:
            # Send a text message to trigger the conversation turn
            message_to_send = {"persona_id": 1, "text_message": "Hello"}
            websocket.send_json(message_to_send)

            # The orchestrator immediately sends the user bubble and AI placeholder
            user_bubble = websocket.receive_text()
            assert 'id="user-message-text-' in user_bubble
            assert "Hello" in user_bubble

            ai_placeholder = websocket.receive_text()
            assert 'id="ai-message-streaming-' in ai_placeholder

            # Then, it sends fragments based on the service's events
            user_transcription_chunk = websocket.receive_text()
            assert 'hx-swap-oob="innerHTML:#user-message-text-' in user_transcription_chunk
            assert ">Hello<" in user_transcription_chunk

            ai_text_chunk = websocket.receive_text()
            assert 'hx-swap-oob="beforeend:#ai-message-streaming-' in ai_text_chunk
            assert ">Hi there!<" in ai_text_chunk

        # Verify the service was called correctly
        conversation_service_mock.run_conversation_turn.assert_called_once()
        call_args = conversation_service_mock.run_conversation_turn.call_args.kwargs
        assert call_args["language_profile_id"] == language_profile_id
        assert call_args["user_message_data"] == "Hello"
