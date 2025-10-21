from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx

from app.core.templating import templates
from app.personas.dependencies import get_persona_page_service, get_persona_service
from app.personas.schemas import PersonaCreate, PersonaUpdate
from app.personas.services import PersonaPageService, PersonaService

router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="view_personas")
async def view_personas(
    request: Request,
    service: PersonaPageService = Depends(get_persona_page_service),
):
    page_data = service.get_personas_page_data()
    return templates.TemplateResponse(
        "personas/pages/main.html", {"request": request, **page_data}
    )


@router.post("/", name="create_persona")
@htmx("personas/partials/persona_item")
async def create_persona(
    request: Request,
    form_data: Annotated[PersonaCreate, Form()],
    service: PersonaService = Depends(get_persona_service),
):
    new_persona = service.create_persona(persona_in=form_data)
    return {"persona": new_persona}


@router.delete("/{persona_id}", name="delete_persona")
async def delete_persona(
    persona_id: int,
    service: PersonaService = Depends(get_persona_service),
):
    service.delete_persona(persona_id=persona_id)
    return Response(status_code=200)


@router.get("/{persona_id}/edit", name="view_edit_persona_form")
@htmx("personas/partials/edit_persona_form")
async def view_edit_persona_form(
    request: Request,
    persona_id: int,
    service: PersonaService = Depends(get_persona_service),
):
    persona = service.get_persona(persona_id=persona_id)
    return {"persona": persona}


@router.put("/{persona_id}", name="update_persona")
@htmx("personas/partials/persona_item")
async def update_persona(
    request: Request,
    persona_id: int,
    form_data: Annotated[PersonaUpdate, Form()],
    service: PersonaService = Depends(get_persona_service),
):
    updated_persona = service.update_persona(
        persona_id=persona_id, persona_in=form_data
    )
    return {"persona": updated_persona}


@router.get("/{persona_id}", name="get_persona")
@htmx("personas/partials/persona_item")
async def get_persona(
    request: Request,
    persona_id: int,
    service: PersonaService = Depends(get_persona_service),
):
    persona = service.get_persona(persona_id=persona_id)
    return {"persona": persona}