from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx

from app.core.templating import templates
from app.settings.dependencies import get_settings_page_service, get_settings_service
from app.settings.schemas import SettingsUpdate
from app.settings.services import SettingsPageService, SettingsService

router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="view_settings")
async def view_settings(
    request: Request, service: SettingsPageService = Depends(get_settings_page_service)
):
    page_data = service.get_settings_page_data()
    return templates.TemplateResponse(
        "settings/pages/main.html", {"request": request, **page_data}
    )


@router.post("/", name="update_settings")
@htmx("settings/partials/settings_content")
async def handle_update_settings(
    request: Request,
    form_data: Annotated[SettingsUpdate, Form()],
    service: SettingsService = Depends(get_settings_service),
):
    updated_settings = service.update_settings(settings_in=form_data)
    return {"settings": updated_settings}
