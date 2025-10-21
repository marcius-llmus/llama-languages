from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import HTMLResponse
from fastapi_htmx import htmx

from app.core.templating import templates
from app.language_profiles.dependencies import (
    get_language_profile_page_service,
    get_language_profile_service,
)
from app.language_profiles.schemas import (
    LanguageProfileCreate,
    LanguageProfileUpdate,
    PracticeTopicCreate,
)
from app.language_profiles.services import (
    LanguageProfilePageService,
    LanguageProfileService,
)

router = APIRouter()


@router.get("/", response_class=HTMLResponse, name="view_language_profiles")
async def view_language_profiles(
    request: Request,
    service: LanguageProfilePageService = Depends(get_language_profile_page_service),
):
    page_data = service.get_language_profiles_page_data()
    return templates.TemplateResponse(
        "language_profiles/pages/main.html", {"request": request, **page_data}
    )


@router.post("/", name="create_language_profile")
@htmx("language_profiles/partials/language_profile_item")
async def create_language_profile(
    request: Request,
    form_data: Annotated[LanguageProfileCreate, Form()],
    service: LanguageProfileService = Depends(get_language_profile_service),
):
    new_profile = service.create_language_profile(profile_in=form_data)
    return {"language_profile": new_profile}


@router.delete("/{profile_id}", name="delete_language_profile")
async def delete_language_profile(
    profile_id: int,
    service: LanguageProfileService = Depends(get_language_profile_service),
):
    service.delete_language_profile(profile_id=profile_id)
    return Response(status_code=200)


@router.get("/{profile_id}/edit", name="view_edit_language_profile_form")
@htmx("language_profiles/partials/edit_language_profile_form")
async def view_edit_language_profile_form(
    request: Request,
    profile_id: int,
    service: LanguageProfileService = Depends(get_language_profile_service),
):
    profile = service.get_language_profile(profile_id=profile_id)
    return {"language_profile": profile}


@router.patch("/{profile_id}", name="update_language_profile")
@htmx("language_profiles/partials/language_profile_item")
async def update_language_profile(
    request: Request,
    profile_id: int,
    form_data: Annotated[LanguageProfileUpdate, Form()],
    service: LanguageProfileService = Depends(get_language_profile_service),
):
    updated_profile = service.update_language_profile(
        profile_id=profile_id, profile_in=form_data
    )
    return {"language_profile": updated_profile}


@router.get("/{profile_id}", name="get_language_profile")
@htmx("language_profiles/partials/language_profile_item")
async def get_language_profile(
    request: Request,
    profile_id: int,
    service: LanguageProfileService = Depends(get_language_profile_service),
):
    profile = service.get_language_profile(profile_id=profile_id)
    return {"language_profile": profile}


@router.post("/{profile_id}/topics", name="add_practice_topic")
@htmx("language_profiles/partials/practice_topic_item")
async def add_practice_topic(
    request: Request,
    profile_id: int,
    form_data: Annotated[PracticeTopicCreate, Form()],
    service: LanguageProfileService = Depends(get_language_profile_service),
):
    new_topic = service.add_topic_to_profile(profile_id=profile_id, topic_in=form_data)
    return {"topic": new_topic}


@router.delete("/topics/{topic_id}", name="delete_practice_topic")
async def delete_practice_topic(
    topic_id: int,
    service: LanguageProfileService = Depends(get_language_profile_service),
):
    service.delete_topic(topic_id=topic_id)
    return Response(status_code=200)
