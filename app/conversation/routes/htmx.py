from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.core.templating import templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="view_conversation")
async def view_conversation(request: Request):
    return templates.TemplateResponse(
        "conversation/pages/main.html", {"request": request}
    )