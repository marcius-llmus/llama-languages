import os
import uuid
import tempfile
import wave
import logging

from llama_index.core import PromptTemplate

from llama_index.core.llms import ChatMessage, DocumentBlock, MessageRole, TextBlock
from llama_index.llms.google_genai import GoogleGenAI
from workflows import Workflow, Context, step
from workflows.events import StartEvent, StopEvent

from app.clients.elevenlabs.elevenlabs_tts import ElevenLabsTTS
from app.conversation.schemas import FeedbackResponse
from app.core.config import settings
from app.language_profiles.services import LanguageProfileService
from app.personas.services import PersonaService
from app.settings.services import SettingsService

from app.conversation.events import (
    AIAudioChunkGenerated,
    FeedbackGenerated,
    AIAudioSaved,
    PromptReady,
    FullResponseGenerated,
    AITextChunkGenerated,
    UserMessageReady,
    AudioInputReceived,
    UserTranscriptionChunkGenerated,
)

logger = logging.getLogger(__name__)


class ConversationWorkflow(Workflow):
    def __init__(
        self,
        settings_service: SettingsService,
        persona_service: PersonaService,
        language_profile_service: LanguageProfileService,
        llm: GoogleGenAI,
        elevenlabs_tts: ElevenLabsTTS,
    ):
        super().__init__()
        self.settings_service = settings_service
        self.persona_service = persona_service
        self.language_profile_service = language_profile_service
        self.llm = llm
        self.elevenlabs_tts = elevenlabs_tts
        self.history: list[ChatMessage] = []

    @step
    async def process_user_input(
            self, ctx: Context, ev: StartEvent
    ) -> UserMessageReady | AudioInputReceived:
        """
        Acts as a branching step.
        - For text input, it passes the message to the conversational workflow.
        - For audio input, it passes the bytes to the direct transcription-to-speech workflow.
        """
        logger.info("Step: process_user_input - Starting.")
        user_input: str | bytes = ev.input["user_message_data"]
        persona_id: int = ev.input["persona_id"]
        language_profile_id: int = ev.input["language_profile_id"]

        if isinstance(user_input, str):
            return UserMessageReady(
                text=user_input,
                persona_id=persona_id,
                language_profile_id=language_profile_id,
            )
        elif isinstance(user_input, bytes):
            logger.info("Input is audio. Emitting AudioInputReceived.")
            return AudioInputReceived(
                audio_bytes=user_input,
                persona_id=persona_id,
                language_profile_id=language_profile_id,
            )
        else:
            err_msg = f"Unsupported user input type: {type(user_input)}"
            logger.error(err_msg)
            raise ValueError(err_msg)

    @step
    async def transcribe_audio_input(self, ctx: Context, ev: AudioInputReceived) -> UserMessageReady:
        """Transcribes the user's audio and passes the text to the conversational workflow."""
        logger.info("Step: transcribe_audio_input - Starting.")
        with tempfile.NamedTemporaryFile(
                delete=True, suffix=".wav"
        ) as temp_audio_file:
            temp_audio_file.write(ev.audio_bytes)
            temp_audio_file.flush()

            messages = [
                ChatMessage(role=MessageRole.USER, blocks=[
                    DocumentBlock(path=temp_audio_file.name, document_mimetype="audio/wav"),
                    TextBlock(text="Transcribe this audio.")
                ])
            ]
            response_stream = await self.llm.astream_chat(messages)

            # first we get transcription and the chunks of transcription we send to user
            full_transcription = ""
            async for r in response_stream:
                full_transcription += r.delta
                ctx.write_event_to_stream(UserTranscriptionChunkGenerated(delta=r.delta))
            logger.info("Finished transcription stream from LLM.")

        # the full transcription follows in the workflow to be sent to llm
        return UserMessageReady(
            text=full_transcription,
            persona_id=ev.persona_id,
            language_profile_id=ev.language_profile_id,
        )

    @step
    async def construct_prompt(self, ctx: Context, ev: UserMessageReady) -> PromptReady:
        """
        Gathers all data and builds the final prompt for the LLM based on the processed user text.
        """
        logger.info(f"Step: construct_prompt - Starting for user message: '{ev.text[:50]}...'")
        self.history.append(ChatMessage(role=MessageRole.USER, content=ev.text))

        persona = self.persona_service.get_persona(ev.persona_id)
        app_settings = self.settings_service.get_settings()

        system_prompt = f"""
Persona: {persona.prompt}
Global Feedback Rules: {app_settings.evaluation_prompt}
---
You are acting as the persona.
"""

        messages = [
            ChatMessage(role=MessageRole.SYSTEM, content=system_prompt.strip())
        ] + self.history

        logger.info("Prompt constructed. Emitting PromptReady.")
        return PromptReady(
            messages=messages,
            voice_id=app_settings.voice_id,
            user_message_text=ev.text,
            persona_id=ev.persona_id,
            language_profile_id=ev.language_profile_id,
        )

    @step
    async def stream_ai_response(self, ctx: Context, ev: PromptReady) -> FullResponseGenerated:
        """
        Streams response text from LLM to the UI, and simultaneously streams that text
        to ElevenLabs to generate audio in real-time. Also emits the full audio bytes
        when done, and returns the full response text for feedback generation.
        """
        logger.info("Step: stream_ai_response - Starting.")

        response_stream = await self.llm.astream_chat(ev.messages)

        full_response_text = ""

        # it is a bit weird, but the only way to handle audio from text
        # chunks is passing the generator to the audio generator
        async def text_generator():
            nonlocal full_response_text
            async for r in response_stream:
                delta = r.delta or ""
                full_response_text += delta
                if delta:
                    ctx.write_event_to_stream(AITextChunkGenerated(delta=delta))
                    yield delta

        all_audio_bytes = b""
        logger.info("Consuming audio stream from TTS client...")
        try:
            audio_stream = self.elevenlabs_tts.stream(text_generator())
            async for chunk in audio_stream:
                all_audio_bytes += chunk
                ctx.write_event_to_stream(AIAudioChunkGenerated(chunk=chunk))
        except Exception as e:
            logger.error(
                f"Error during ElevenLabs WebSocket streaming: {e}", exc_info=True
            )
            all_audio_bytes = b""

        logger.info("Finished streaming audio from TTS client.")

        self.history.append(
            ChatMessage(role=MessageRole.ASSISTANT, content=full_response_text)
        )
        logger.info(f"History updated with: '{full_response_text[:50]}...'")

        return FullResponseGenerated(
            ai_response_text=full_response_text,
            user_message_text=ev.user_message_text,
            audio_bytes=all_audio_bytes,
            persona_id=ev.persona_id,
            language_profile_id=ev.language_profile_id,
        )

    @step
    async def save_audio(
        self, ctx: Context, ev: FullResponseGenerated
    ) -> AIAudioSaved:
        """
        Saves the complete audio bytes to a file and passes data to the feedback step.
        """
        logger.info("Step: save_audio - Starting.")
        audio_url = None
        if ev.audio_bytes:
            output_dir = settings.AUDIO_OUTPUT_DIR
            os.makedirs(output_dir, exist_ok=True)
            file_name = f"{uuid.uuid4()}.wav"
            file_path = os.path.join(output_dir, file_name)

            with wave.open(file_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit PCM
                wf.setframerate(24000)
                wf.writeframes(ev.audio_bytes)
            audio_url = f"/static/audio/{file_name}"
            logger.info(f"Audio saved to {file_path}. URL: {audio_url}")

            ctx.write_event_to_stream(AIAudioSaved(audio_url=audio_url))
            logger.info("Audio saved event dispatched.")
        else:
            logger.info("No audio bytes to save.")

        return AIAudioSaved(audio_url=audio_url)

    @step
    async def generate_feedback(
        self, ctx: Context, ev: FullResponseGenerated
    ) -> FeedbackGenerated:
        """Generates feedback for the user's message and ends the workflow."""
        logger.info("Step: generate_feedback - Starting.")

        persona = self.persona_service.get_persona(ev.persona_id)
        app_settings = self.settings_service.get_settings()

        feedback_prompt_template = PromptTemplate(
            "You are an AI language coach. Your task is to provide feedback on a user's message.\n"
            "The user is practicing a language.\n"
            "Analyze the user's message for spelling mistakes, grammatical errors, and suggest better ways to phrase things.\n"
            "Your feedback should be concise and helpful.\n"
            "Do not generate a conversational response. Only generate feedback.\n\n"
            "Persona of conversational partner: {persona_prompt}\n"
            "Global Feedback Rules: {evaluation_prompt}\n"
            "---\n"
            "User's message: \"{user_message_text}\"\n"
            "---\n"
            "Now, provide feedback on the user's message based on the rules. If there are no errors, you must return an empty list of feedback."
        )

        feedbacks = []
        try:
            response = await self.llm.astructured_predict(
                FeedbackResponse,
                feedback_prompt_template,
                persona_prompt=persona.prompt,
                evaluation_prompt=app_settings.evaluation_prompt,
                user_message_text=ev.user_message_text,
            )
            if response.feedback:
                logger.info(f"Generated feedback: {response.feedback}")
                feedbacks = response.feedback
        except Exception as e:
            logger.error(f"Failed to generate feedback: {e}", exc_info=True)

        # Always emit the event. An empty list signifies analysis is complete with no feedback items.
        ctx.write_event_to_stream(FeedbackGenerated(feedbacks=feedbacks))
        logger.info("Step: generate_feedback - Finished.")
        return FeedbackGenerated(feedbacks=feedbacks)

    @step
    async def gather(self, ctx: Context, ev: AIAudioSaved | FeedbackGenerated) -> StopEvent | None:
        data = ctx.collect_events(ev, [AIAudioSaved, FeedbackGenerated])
        if data is None:
            return None

        return StopEvent()
