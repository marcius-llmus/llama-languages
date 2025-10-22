from fastapi import Depends
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.tools.elevenlabs import ElevenLabsToolSpec

from app.core.config import settings
from app.language_profiles.dependencies import get_language_profile_service
from app.language_profiles.services import LanguageProfileService
from app.personas.dependencies import get_persona_service
from app.personas.services import PersonaService
from app.settings.dependencies import get_settings_service
from app.settings.services import SettingsService
from app.conversation.services import ConversationService, WebSocketOrchestratorService
from app.conversation.workflows import ConversationWorkflow


def get_gemini_llm() -> GoogleGenAI:
    return GoogleGenAI(model="gemini-2.5-pro-preview-06-05", api_key=settings.GOOGLE_API_KEY)


def get_elevenlabs_client() -> ElevenLabsToolSpec:
    return ElevenLabsToolSpec(api_key=settings.ELEVENLABS_API_KEY)


def get_conversation_workflow(
    settings_service: SettingsService = Depends(get_settings_service),
    persona_service: PersonaService = Depends(get_persona_service),
    language_profile_service: LanguageProfileService = Depends(
        get_language_profile_service
    ),
    llm: GoogleGenAI = Depends(get_gemini_llm),
    tts: ElevenLabsToolSpec = Depends(get_elevenlabs_client),
) -> ConversationWorkflow:
    return ConversationWorkflow(
        settings_service=settings_service,
        persona_service=persona_service,
        language_profile_service=language_profile_service,
        llm=llm,
        tts=tts,
    )


def get_conversation_service(
    workflow: ConversationWorkflow = Depends(get_conversation_workflow),
) -> ConversationService:
    return ConversationService(workflow=workflow)


def get_websocket_orchestrator_service(
    conversation_service: ConversationService = Depends(get_conversation_service),
) -> WebSocketOrchestratorService:
    return WebSocketOrchestratorService(conversation_service=conversation_service)
