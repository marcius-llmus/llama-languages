from fastapi import APIRouter, Depends, Request, WebSocket
from fastapi.responses import HTMLResponse

from app.commons.websocket_conn_manager import WebSocketConnectionManager
from app.core.templating import templates
from app.language_profiles.dependencies import get_language_profile_service
from app.language_profiles.services import LanguageProfileService
from app.personas.dependencies import get_persona_service
from app.personas.services import PersonaService
from app.conversation.services import ConversationService
from app.conversation.dependencies import get_conversation_service
from app.conversation.presentation import WebSocketOrchestrator

router = APIRouter()


@router.get(
    "/{language_profile_id}", response_class=HTMLResponse, name="view_conversation"
)
async def view_conversation_page(
    request: Request,
    language_profile_id: int,
    service: LanguageProfileService = Depends(
        get_language_profile_service
    ),
):
    language_profile = service.get_language_profile(language_profile_id)
    if not language_profile:
        return HTMLResponse("Language profile not found.", status_code=404)
    context = {
        "request": request,
        "language_profile": language_profile,
    }
    return templates.TemplateResponse("conversation/pages/main.html", context)


# note: this ws has no authorization of personas etc. by user
@router.websocket("/ws/{language_profile_id}")
async def conversation_websocket(
    websocket: WebSocket,
    language_profile_id: int,
    conversation_service: ConversationService = Depends(get_conversation_service), # todo check db conn
):
    ws_manager = WebSocketConnectionManager(websocket)
    await ws_manager.connect()
    orchestrator = WebSocketOrchestrator(
        conversation_service=conversation_service,
        ws_manager=ws_manager,
    )
    await orchestrator.handle_connection(language_profile_id)
