import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi_htmx import htmx_init

from app.core.templating import templates
from app.conversation.routes.htmx import router as conversation_htmx_router
from app.language_profiles.routes.htmx import router as language_profiles_router
from app.personas.routes.htmx import router as personas_router
from app.settings.routes.htmx import router as settings_router
from app.core.db import engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application initialization...")
    from sqlalchemy.orm import Session
    from app.settings.utils import initialize_application_settings
    
    with Session(engine) as db:
        initialize_application_settings(db)

    logger.info("=" * 70)
    logger.info("Access the application in your browser at the appropriate localhost or audio input won't work")
    logger.info("=" * 70)

    yield
    logger.info("Application shutdown.")

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

htmx_init(templates=templates, file_extension="html")

# HTMX Routes
app.include_router(personas_router, prefix="/personas", tags=["personas_htmx"])
app.include_router(language_profiles_router, prefix="/language-profiles", tags=["language_profiles_htmx"])
app.include_router(settings_router, prefix="/settings", tags=["settings_htmx"])
app.include_router(conversation_htmx_router, prefix="/conversation", tags=["conversation_htmx"])
# ---

@app.get("/", include_in_schema=False)
async def root(request: Request):
    return RedirectResponse(request.url_for("view_personas"))
