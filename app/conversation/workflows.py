import os
import uuid

from llama_index.core.llms import ChatMessage
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.tools.elevenlabs import ElevenLabsToolSpec
from workflows import Workflow, Context, step
from workflows.events import StartEvent, StopEvent

from app.core.config import settings
from app.language_profiles.services import LanguageProfileService
from app.personas.services import PersonaService
from app.settings.services import SettingsService

from app.conversation.events import (
    AudioReady,
    AudioGenerated,
    PromptReady,
    FullResponseGenerated,
    TextChunkGenerated,
)


class ConversationWorkflow(Workflow):
    def __init__(
        self,
        settings_service: SettingsService,
        persona_service: PersonaService,
        language_profile_service: LanguageProfileService,
        llm: GoogleGenAI,
        tts: ElevenLabsToolSpec,
    ):
        super().__init__()
        self.settings_service = settings_service
        self.persona_service = persona_service
        self.language_profile_service = language_profile_service
        self.llm = llm
        self.tts = tts
        self.history: list[ChatMessage] = []

    @step
    async def construct_prompt(
        self, ctx: Context, ev: StartEvent
    ) -> PromptReady:
        """
        Gathers all data and builds the final prompt for the LLM.
        """
        user_message: str = ev.input["user_message"]
        persona_id: int = ev.input["persona_id"]
        focus_topic_id: int | None = ev.input["focus_topic_id"]
        language_profile_id: int = ev.input["language_profile_id"]

        # Add user message to history for this turn
        self.history.append(ChatMessage(role="user", content=user_message))

        persona = self.persona_service.get_persona(persona_id)
        app_settings = self.settings_service.get_settings()

        topic_prompt_part = ""
        if focus_topic_id:
            profile = self.language_profile_service.get_language_profile(
                language_profile_id
            )
            if profile:
                topic = next(
                    (t for t in profile.practice_topics if t.id == focus_topic_id), None
                )
                if topic:
                    topic_prompt_part = f"""
Current Focus: {topic.topic_name}
Your task is to steer the conversation towards this focus topic.
Then, evaluate the user's last message based on the focus, following the feedback rules.
"""

        system_prompt = f"""
Persona: {persona.prompt}
Global Feedback Rules: {app_settings.evaluation_prompt}
{topic_prompt_part}
---
You are acting as the persona.
"""

        messages = [
            ChatMessage(role="system", content=system_prompt.strip())
        ] + self.history

        return PromptReady(messages=messages, voice_id=app_settings.voice_id)

    @step
    async def stream_llm_response(
        self, ctx: Context, ev: PromptReady
    ) -> FullResponseGenerated:
        """Streams the LLM response, emitting events for each chunk."""
        full_response = ""
        response_stream = await self.llm.astream_chat(ev.messages)
        async for r in response_stream:
            full_response += r.delta
            ctx.write_event_to_stream(TextChunkGenerated(delta=r.delta))

        return FullResponseGenerated(
            full_response=full_response, voice_id=ev.voice_id
        )

    @step
    def generate_audio(
        self, ctx: Context, ev: FullResponseGenerated
    ) -> AudioGenerated:
        """Generates audio from the full response and emits the URL."""
        os.makedirs(settings.AUDIO_OUTPUT_DIR, exist_ok=True)
        output_filename = f"{uuid.uuid4()}.wav"
        output_file_path = os.path.join(settings.AUDIO_OUTPUT_DIR, output_filename)

        tts_kwargs = {"text": ev.full_response, "output_path": output_file_path, "voice_id": ev.voice_id}

        self.tts.text_to_speech(**tts_kwargs)
        audio_url = f"/{output_file_path}"
        ctx.write_event_to_stream(AudioReady(audio_url=audio_url))

        return AudioGenerated(full_response=ev.full_response)

    @step
    def update_history(self, ctx: Context, ev: AudioGenerated) -> StopEvent:
        """Adds the assistant's final response to the history for the next turn."""
        self.history.append(ChatMessage(role="assistant", content=ev.full_response))
        return StopEvent()
