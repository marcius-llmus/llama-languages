from fastapi import Depends
from typing import cast
from llama_index.llms.google_genai import GoogleGenAI

from app.clients.elevenlabs.elevenlabs_client import PatchedAsyncElevenLabs
from app.clients.elevenlabs.elevenlabs_tts import ElevenLabsTTS
from app.clients.elevenlabs.patched_elevenlabs import AsyncRealtimeTextToSpeechClient
from app.core.config import settings
from app.language_profiles.dependencies import get_language_profile_service
from app.language_profiles.services import LanguageProfileService
from app.personas.dependencies import get_persona_service
from app.personas.services import PersonaService
from app.settings.dependencies import get_settings_service
from app.settings.services import SettingsService
from app.conversation.services import ConversationService
from app.conversation.workflows import ConversationWorkflow


def get_gemini_llm() -> GoogleGenAI:
    return GoogleGenAI(model="gemini-2.5-flash", api_key=settings.GOOGLE_API_KEY)


def get_elevenlabs_async_client() -> PatchedAsyncElevenLabs:
    return PatchedAsyncElevenLabs(api_key=settings.ELEVENLABS_API_KEY)


def get_realtime_tts_client(
    client: PatchedAsyncElevenLabs = Depends(get_elevenlabs_async_client),
) -> AsyncRealtimeTextToSpeechClient:
    return client.realtime_text_to_speech


def get_elevenlabs_tts_client(
    realtime_client: AsyncRealtimeTextToSpeechClient = Depends(
        get_realtime_tts_client
    ),
    settings_service: SettingsService = Depends(get_settings_service),
) -> ElevenLabsTTS:
    app_settings = settings_service.get_settings()
    if not app_settings.voice_id:
        raise ValueError("ElevenLabs Voice ID is not configured in settings.")
    return ElevenLabsTTS(
        realtime_client=realtime_client, voice_id=cast(str, app_settings.voice_id)
    )


def get_conversation_workflow(
    settings_service: SettingsService = Depends(get_settings_service),
    persona_service: PersonaService = Depends(get_persona_service),
    language_profile_service: LanguageProfileService = Depends(
        get_language_profile_service
    ),
    llm: GoogleGenAI = Depends(get_gemini_llm),
    elevenlabs_tts: ElevenLabsTTS = Depends(get_elevenlabs_tts_client),
) -> ConversationWorkflow:
    return ConversationWorkflow(
        settings_service=settings_service,
        persona_service=persona_service,
        language_profile_service=language_profile_service,
        llm=llm,
        elevenlabs_tts=elevenlabs_tts,
    )


def get_conversation_service(
    workflow: ConversationWorkflow = Depends(get_conversation_workflow),
) -> ConversationService:
    return ConversationService(workflow=workflow)