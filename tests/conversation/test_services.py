import pytest
from unittest.mock import MagicMock, AsyncMock

from app.conversation.events import (
    AIAudioChunkGenerated,
    AIAudioSaved,
    FeedbackGenerated,
    AITextChunkGenerated,
    UserTranscriptionChunkGenerated,
)
from app.conversation.schemas import Feedback
from app.conversation.enums import ConversationEventType, FeedbackType
from app.conversation.services import ConversationService


class MockWorkflowHandler:
    """Mock handler that supports both stream_events() and awaiting."""
    def __init__(self, events):
        self.events = events
    
    def stream_events(self):
        async def generator():
            for event in self.events:
                yield event
        return generator()
    
    def __await__(self):
        async def complete():
            return None
        return complete().__await__()


class TestConversationService:
    @pytest.mark.asyncio
    async def test_run_conversation_turn(self, conversation_service: ConversationService, conversation_workflow_mock: MagicMock):
        mock_feedbacks = [Feedback(type=FeedbackType.TIP, reasoning="Good pronunciation")]
        # Create a sequence of mock events to be "emitted" by the workflow
        events_to_emit = [
            AITextChunkGenerated(delta="Hello"),
            UserTranscriptionChunkGenerated(delta="User said"),
            FeedbackGenerated(feedbacks=mock_feedbacks),
            AIAudioChunkGenerated(chunk=b"audio_bytes"),
            AIAudioSaved(audio_url="/audio/test.mp3"),
        ]

        mock_handler = MockWorkflowHandler(events_to_emit)
        conversation_workflow_mock.run.return_value = mock_handler

        # 2. Act
        # Collect all dictionaries yielded by the service
        results = [
            result
            async for result in conversation_service.run_conversation_turn(
                user_message_data="test audio",
                persona_id=1,
                language_profile_id=2,
                practice_topic_id=3,
            )
        ]

        conversation_workflow_mock.run.assert_called_once()
        call_args = conversation_workflow_mock.run.call_args.kwargs
        assert call_args["input"]["user_message_data"] == "test audio"

        assert len(results) == len(events_to_emit)
        assert results[0] == {"type": ConversationEventType.AI_TEXT_CHUNK_GENERATED, "data": "Hello"}
        assert results[1] == {"type": ConversationEventType.USER_TRANSCRIPTION_CHUNK_GENERATED, "data": "User said"}
        assert results[2] == {"type": ConversationEventType.FEEDBACK_GENERATED, "data": mock_feedbacks}
        assert results[3] == {"type": ConversationEventType.AI_AUDIO_CHUNK_GENERATED, "data": b"audio_bytes"}
        assert results[4] == {"type": ConversationEventType.AI_AUDIO_READY, "data": {"audio_url": "/audio/test.mp3"}}