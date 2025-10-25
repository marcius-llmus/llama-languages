import base64
import logging
from typing import Any, Callable, Coroutine
import uuid

from fastapi import WebSocketDisconnect

from app.commons.websocket_conn_manager import WebSocketConnectionManager
from app.conversation.enums import ConversationEventType, FeedbackType
from app.conversation.services import ConversationService
from app.core.templating import templates

logger = logging.getLogger(__name__)

Handler = Callable[[Any, str], Coroutine[Any, Any, None]]


class WebSocketOrchestrator:
    def __init__(
        self,
        conversation_service: ConversationService,
        ws_manager: WebSocketConnectionManager,
    ):
        self.conversation_service = conversation_service
        self.ws_manager = ws_manager
        self.transcription_started_turns: set[str] = set()
        self.event_handlers: dict[ConversationEventType, Handler] = {
            ConversationEventType.AI_TEXT_CHUNK_GENERATED: self._render_ai_text_chunk,
            ConversationEventType.FEEDBACK_GENERATED: self._render_user_message_feedback,
            ConversationEventType.AI_AUDIO_CHUNK_GENERATED: self._send_ai_audio_chunk,
            ConversationEventType.AI_AUDIO_READY: self._render_ai_audio_player,
            ConversationEventType.USER_TRANSCRIPTION_CHUNK_GENERATED: self._render_user_transcription_chunk,
        }

    async def _process_chunk(
        self, chunk: dict, turn_id: str
    ):
        event_type = chunk["type"]
        event_data = chunk["data"]
        handler = self.event_handlers.get(event_type)
        if not handler:
            raise ValueError(f"Unknown event type: {chunk['type']}")
        await handler(event_data, turn_id)

    async def handle_connection(
        self, language_profile_id: int
    ):
        logger.info(
            f"WebSocket connection established for language_profile_id={language_profile_id}"
        )
        try:
            while True:
                data = await self.ws_manager.receive_json()
                logger.info("Received JSON data from client.")

                persona_id = data["persona_id"]
                practice_topic_id = data.get("practice_topic_id")

                if text_message := data.get("text_message"):
                    logger.info("Received text message from client.")
                    user_message_data = text_message
                elif audio_data := data.get("audio_message"):
                    logger.info("Received audio message from client.")
                    header, encoded = audio_data.split(",", 1)
                    user_message_data = base64.b64decode(encoded)
                else:
                    raise ValueError("Invalid data received from client.")

                turn_id = str(uuid.uuid4())
                logger.info(f"Initiating turn {turn_id}.")

                await self._render_user_bubble(user_message_data, turn_id)

                await self._render_ai_bubble_place_holder(turn_id)

                stream = self.conversation_service.run_conversation_turn(
                    user_message_data=user_message_data,
                    persona_id=persona_id,
                    language_profile_id=language_profile_id,
                    practice_topic_id=practice_topic_id,
                )

                async for chunk in stream:
                    await self._process_chunk(chunk, turn_id)

        except WebSocketDisconnect:
            logger.info("Client disconnected. Connection handled gracefully.")
        except Exception as e:
            logger.error(f"An error occurred in WebSocket: {e}", exc_info=True)

    async def _render_user_bubble(
        self, message: str | bytes, turn_id: str
    ):
        is_text_message = isinstance(message, str)
        template = templates.get_template(
            "conversation/partials/user_message_bubble.html",
        ).render(
            {"message": message if is_text_message else None, "turn_id": turn_id}
        )
        await self.ws_manager.send_html(template)

    async def _render_ai_bubble_place_holder(
        self, turn_id: str
    ):
        template = templates.get_template(
            "conversation/partials/ai_message_bubble.html"
        ).render({"turn_id": turn_id})
        await self.ws_manager.send_html(template)

    async def _render_ai_text_chunk(
        self, data: Any, turn_id: str
    ):
        template = templates.get_template(
            "conversation/partials/ai_message_streaming_token.html"
        ).render({"token": data, "turn_id": turn_id})
        await self.ws_manager.send_html(template)

    async def _render_user_message_feedback(
        self, data: Any, turn_id: str
    ):
        feedbacks_to_show = data
        if not feedbacks_to_show:
            template = templates.get_template(
                "conversation/partials/user_message_success.html"
            ).render({"turn_id": turn_id})
        else:
            feedback_level = "green"  # should never be green, unless a new type is added but not mapped here
            feedback_types = {f.type for f in feedbacks_to_show}
            if FeedbackType.CORRECTION in feedback_types:
                feedback_level = "red"
            elif feedback_types.intersection(
                {FeedbackType.SUGGESTION, FeedbackType.TIP}
            ):
                feedback_level = "yellow"
            elif FeedbackType.PRONUNCIATION in feedback_types:
                feedback_level = "teal"

            context = {
                "turn_id": turn_id,
                "feedback_level": feedback_level,
                "feedbacks_to_show": feedbacks_to_show,
            }
            template = templates.get_template(
                "conversation/partials/user_message_feedback.html"
            ).render(context)
        await self.ws_manager.send_html(template)

    async def _send_ai_audio_chunk(
        self, data: Any, _turn_id: str
    ):
        await self.ws_manager.send_bytes(data)

    async def _render_ai_audio_player(
        self, data: Any, turn_id: str
    ):
        template = templates.get_template(
            "conversation/partials/audio_player.html"
        ).render({"audio_url": data["audio_url"], "turn_id": turn_id})
        await self.ws_manager.send_html(template)

    async def _render_user_transcription_chunk(
        self, data: Any, turn_id: str
    ):
        if turn_id not in self.transcription_started_turns:
            # First chunk, replace "Transcribing..."
            template = templates.get_template(
                "conversation/partials/user_message_transcription.html"
            ).render({"transcription": data, "turn_id": turn_id})
            self.transcription_started_turns.add(turn_id)
        else:
            # Subsequent chunks, append
            template = templates.get_template(
                "conversation/partials/user_message_streaming_token.html"
            ).render({"token": data, "turn_id": turn_id})
        await self.ws_manager.send_html(template)