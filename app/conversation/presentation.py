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
        manager: WebSocketConnectionManager,
    ):
        self.conversation_service = conversation_service
        self.manager = manager
        self.event_handlers: dict[ConversationEventType, Handler] = {
            ConversationEventType.AI_TEXT_CHUNK_GENERATED: self._render_ai_text_chunk,
            ConversationEventType.FEEDBACK_GENERATED: self._render_user_message_feedback,
            ConversationEventType.AI_AUDIO_CHUNK_GENERATED: self._send_ai_audio_chunk,
            ConversationEventType.AI_AUDIO_READY: self._render_ai_audio_player,
            ConversationEventType.USER_TRANSCRIPTION_CHUNK_GENERATED: self._render_user_transcription_chunk,
        }

    async def _process_and_render_event_chunk(
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
                data = await self.manager.receive_json()
                logger.info("Received JSON data from client.")

                persona_id = data["persona_id"]

                if text_message := data.get("text_message"):
                    logger.info("Received text message from client.")
                    user_message_data = text_message
                    is_conversational = True
                elif audio_data := data.get("audio_message"):
                    logger.info("Received audio message from client.")
                    header, encoded = audio_data.split(",", 1)
                    user_message_data = base64.b64decode(encoded)
                    is_conversational = False
                else:
                    raise ValueError("Invalid data received from client.")

                turn_id = str(uuid.uuid4())
                logger.info(f"Initiating turn {turn_id}.")

                await self._render_user_bubble_with_loading_state(
                    user_message_data if isinstance(user_message_data, str) else "",
                    turn_id,
                    is_conversational=is_conversational,
                )

                # This is a temporary solution until personas are properly managed.
                persona_initial = "P"

                await self._render_ai_bubble_place_holder(turn_id, persona_initial)

                stream = self.conversation_service.run_conversation_turn(
                    user_message_data=user_message_data,
                    persona_id=persona_id,
                    language_profile_id=language_profile_id,
                )

                analysis_complete = False
                async for chunk in stream:
                    logger.info(f"Rendering event '{chunk['type']}' for turn_id={turn_id}")
                    if not analysis_complete and is_conversational:
                        # For conversational (text) turns, remove the spinner on the first AI response chunk.
                        await self._render_user_feedback(turn_id, None)
                        analysis_complete = True
                    await self._process_and_render_event_chunk(chunk, turn_id)

        except WebSocketDisconnect:
            logger.info("Client disconnected. Connection handled gracefully.")
        except Exception as e:
            logger.error(f"An error occurred in WebSocket: {e}", exc_info=True)

    async def _render_user_bubble_with_loading_state(
        self, message: str, turn_id: str, is_conversational: bool
    ):
        template = templates.get_template(
            "conversation/partials/user_message_bubble.html",
        ).render(
            {"message": message, "turn_id": turn_id, "is_conversational": is_conversational}
        )
        await self.manager.send_html(template)

    async def _render_ai_bubble_place_holder(
        self, turn_id: str, persona_initial: str
    ):
        template = templates.get_template(
            "conversation/partials/ai_message_bubble.html"
        ).render({"turn_id": turn_id, "persona_initial": persona_initial})
        await self.manager.send_html(template)

    async def _render_user_feedback(
        self, turn_id: str, feedback: dict | None
    ):
        feedback_level = None
        if feedback and feedback.get("type"):
            feedback_type = feedback["type"]
            if feedback_type == FeedbackType.CORRECTION:
                feedback_level = "red"
            elif feedback_type in [FeedbackType.SUGGESTION, FeedbackType.TIP]:
                feedback_level = "yellow"

        context = {
            "turn_id": turn_id,
            "feedback": feedback,
            "feedback_level": feedback_level,
        }
        template = templates.get_template("conversation/partials/user_message_feedback.html").render(context)
        await self.manager.send_html(template)

    async def _render_ai_text_chunk(
        self, data: Any, turn_id: str
    ):
        template = templates.get_template(
            "conversation/partials/streaming_token.html"
        ).render({"token": data, "turn_id": turn_id})
        await self.manager.send_html(template)

    async def _render_user_message_feedback(
        self, data: Any, turn_id: str
    ):
        await self._render_user_feedback(turn_id, data)

    async def _send_ai_audio_chunk(
        self, data: Any, _turn_id: str
    ):
        await self.manager.send_bytes(data)

    async def _render_ai_audio_player(
        self, data: Any, turn_id: str
    ):
        template = templates.get_template(
            "conversation/partials/audio_player.html"
        ).render({"audio_url": data["audio_url"], "turn_id": turn_id})
        await self.manager.send_html(template)

    async def _render_user_transcription_chunk(
        self, data: Any, turn_id: str
    ):
        template = templates.get_template(
            "conversation/partials/user_message_streaming_token.html"
        ).render({"token": data, "turn_id": turn_id})
        await self.manager.send_html(template)