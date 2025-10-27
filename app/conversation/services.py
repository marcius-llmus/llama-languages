import logging
from typing import AsyncGenerator

from app.conversation.enums import ConversationEventType
from app.conversation.events import (
    AIAudioChunkGenerated,
    AIAudioSaved,
    FeedbackGenerated,
    AITextChunkGenerated,
    UserTranscriptionChunkGenerated,
)
from app.conversation.workflows import ConversationWorkflow

logger = logging.getLogger(__name__)


class ConversationService:
    """
    This service works as a translator. The system doesn't understand the workflow
    so we use this service to map the IO and behavior like what events and data is being generated.
    """

    def __init__(self, workflow: ConversationWorkflow):
        self.workflow = workflow

    async def run_conversation_turn(self, *, user_message_data: str | bytes, persona_id: int,
                                    language_profile_id: int, practice_topic_id: int | None) -> AsyncGenerator[dict, None]:

        start_input = {
            "user_message_data": user_message_data,
            "persona_id": persona_id,
            "language_profile_id": language_profile_id,
            "practice_topic_id": practice_topic_id,
        }

        logger.info(f"Starting workflow with input keys: {list(start_input.keys())}")
        handler = self.workflow.run(input=start_input)

        async for event in handler.stream_events():
            if isinstance(event, AITextChunkGenerated):
                yield {"type": ConversationEventType.AI_TEXT_CHUNK_GENERATED, "data": event.delta}
            elif isinstance(event, FeedbackGenerated):
                yield {"type": ConversationEventType.FEEDBACK_GENERATED, "data": event.feedbacks}
            elif isinstance(event, AIAudioChunkGenerated):
                yield {"type": ConversationEventType.AI_AUDIO_CHUNK_GENERATED, "data": event.chunk}
            elif isinstance(event, AIAudioSaved):
                yield {"type": ConversationEventType.AI_AUDIO_READY, "data": {"audio_url": event.audio_url}}
            elif isinstance(event, UserTranscriptionChunkGenerated):
                yield {"type": ConversationEventType.USER_TRANSCRIPTION_CHUNK_GENERATED, "data": event.delta}
            else:
                logger.warning(f"Unknown event type: {event}")
