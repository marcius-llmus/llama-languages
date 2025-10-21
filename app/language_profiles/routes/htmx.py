from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core.templating import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="view_language_profiles")
async def view_language_profiles(request: Request):
    return templates.TemplateResponse(
        "language_profiles/pages/main.html", {"request": request}
    )