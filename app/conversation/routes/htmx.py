from fastapi import APIRouter, Depends, Request, WebSocket
from fastapi.responses import HTMLResponse

from app.core.templating import templates
from app.language_profiles.dependencies import get_language_profile_service
from app.language_profiles.services import LanguageProfileService
from app.personas.dependencies import get_persona_service
from app.personas.services import PersonaService
from app.conversation.connection_manager import WebSocketConnectionManager
from app.conversation.dependencies import get_websocket_orchestrator_service
from app.conversation.services import WebSocketOrchestratorService

router = APIRouter()


@router.get(
    "/{language_profile_id}", response_class=HTMLResponse, name="view_conversation"
)
async def view_conversation_page(
    request: Request,
    language_profile_id: int,
    language_profile_service: LanguageProfileService = Depends(
        get_language_profile_service
    ),
    persona_service: PersonaService = Depends(get_persona_service),
):
    language_profile = language_profile_service.get_language_profile(language_profile_id)
    personas = persona_service.list_personas()
    context = {
        "request": request,
        "language_profile": language_profile,
        "personas": personas,
    }
    return templates.TemplateResponse("conversation/pages/main.html", context)


@router.websocket("/ws/{language_profile_id}")
async def conversation_websocket(
    websocket: WebSocket,
    language_profile_id: int,
    service: WebSocketOrchestratorService = Depends(
        get_websocket_orchestrator_service
    ),
):
    manager = WebSocketConnectionManager(websocket)
    await manager.connect()
    await service.handle_connection(manager, language_profile_id)
