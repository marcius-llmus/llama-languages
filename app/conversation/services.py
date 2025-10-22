from typing import AsyncGenerator
import uuid

from fastapi import WebSocketDisconnect

from app.conversation.enums import ConversationEventType
from app.core.templating import templates
from app.conversation.connection_manager import WebSocketConnectionManager
from app.conversation.constants import STT_NOT_IMPLEMENTED_FALLBACK
from app.conversation.events import (
    AudioReady,
    TextChunkGenerated,
)
from app.conversation.workflows import ConversationWorkflow


class ConversationService:
    def __init__(self, workflow: ConversationWorkflow):
        self.workflow = workflow

    async def process_turn_streaming(
        self,
        *,
        user_message: str,
        persona_id: int,
        focus_topic_id: int | None,
        language_profile_id: int,
    ) -> AsyncGenerator[dict, None]:
        start_input = {
            "user_message": user_message,
            "persona_id": persona_id,
            "focus_topic_id": focus_topic_id,
            "language_profile_id": language_profile_id,
        }

        handler = self.workflow.run(input=start_input)

        async for event in handler.stream_events():
            if isinstance(event, TextChunkGenerated):
                yield {"type": ConversationEventType.TEXT_CHUNK, "data": event.delta}
            elif isinstance(event, AudioReady):
                yield {"type": ConversationEventType.AUDIO_READY, "data": {"audio_url": event.audio_url}}


class WebSocketOrchestratorService:
    def __init__(self, conversation_service: ConversationService):
        self.conversation_service = conversation_service

    async def handle_connection(
        self, manager: WebSocketConnectionManager, language_profile_id: int
    ):
        try:
            while True:
                data = await manager.receive_json()
                user_message = self._process_incoming_data(data)

                turn_id = str(uuid.uuid4())

                await self._render_user_bubble_with_message(user_message, manager)
                await self._render_ai_bubble_place_holder(turn_id, manager) # will be empty at first

                async for chunk in self.conversation_service.process_turn_streaming(
                    user_message=user_message,
                    persona_id=data["persona_id"],
                    focus_topic_id=data["focus_topic_id"],
                    language_profile_id=language_profile_id,
                ):
                    await self._render_ai_message_chunk_in_place_holder(chunk, turn_id, manager)

        except WebSocketDisconnect:
            print("Client disconnected. Connection handled gracefully.")
        except Exception as e:
            print(f"An error occurred in WebSocket: {e}")

    @staticmethod
    def _process_incoming_data(data: dict) -> str:
        if message := data.get("text_message"):
            return message
        raise ValueError(STT_NOT_IMPLEMENTED_FALLBACK)

    @staticmethod
    async def _render_user_bubble_with_message(message: str, manager: WebSocketConnectionManager):
        template = templates.get_template(
            "conversation/partials/user_message_bubble.html"
        ).render({"message": message})
        await manager.send_html(template)

    @staticmethod
    async def _render_ai_bubble_place_holder(turn_id: str, manager: WebSocketConnectionManager):
        template = templates.get_template(
            "conversation/partials/ai_message_bubble.html"
        ).render({"turn_id": turn_id})
        await manager.send_html(template)

    @staticmethod
    async def _render_ai_message_chunk_in_place_holder(chunk: dict, turn_id: str, manager: WebSocketConnectionManager):
        if chunk["type"] == ConversationEventType.TEXT_CHUNK:
            template = templates.get_template(
                "conversation/partials/streaming_token.html"
            ).render({"token": chunk["data"], "turn_id": turn_id})
        elif chunk["type"] == ConversationEventType.AUDIO_READY:
            template = templates.get_template(
                "conversation/partials/audio_player.html"
            ).render({"audio_url": chunk["data"]["audio_url"], "turn_id": turn_id})
        else:
            raise ValueError(f"Unknown message type: {chunk['type']}")

        await manager.send_html(template)
