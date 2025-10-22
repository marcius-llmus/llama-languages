from typing import AsyncGenerator
import uuid

from fastapi import WebSocketDisconnect
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
                yield {"type": "text_chunk", "data": event.delta}
            elif isinstance(event, AudioReady):
                yield {"type": "audio_ready", "data": {"audio_url": event.audio_url}}


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

                user_bubble_html = self._render_user_message(user_message, turn_id)
                await manager.send_html(user_bubble_html)

                async for chunk in self.conversation_service.process_turn_streaming(
                    user_message=user_message,
                    persona_id=data["persona_id"],
                    focus_topic_id=data.get("focus_topic_id"),
                    language_profile_id=language_profile_id,
                ):
                    html_fragment = self._render_chunk(chunk, turn_id)
                    if html_fragment:
                        await manager.send_html(html_fragment)

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
    def _render_user_message(message: str, turn_id: str) -> str:
        user_bubble = templates.get_template(
            "conversation/partials/user_message_bubble.html"
        ).render({"message": message})
        ai_placeholder = templates.get_template(
            "conversation/partials/ai_message_bubble.html"
        ).render({"turn_id": turn_id})
        return user_bubble + "\n" + ai_placeholder

    @staticmethod
    def _render_chunk(chunk: dict, turn_id: str) -> str:
        if chunk["type"] == "text_chunk":
            return templates.get_template(
                "conversation/partials/streaming_token.html"
            ).render({"token": chunk["data"], "turn_id": turn_id})
        elif chunk["type"] == "audio_ready":
            return templates.get_template(
                "conversation/partials/audio_player.html"
            ).render({"audio_url": chunk["data"]["audio_url"], "turn_id": turn_id})
        return ""
