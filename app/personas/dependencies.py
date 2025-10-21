from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.personas.repositories import PersonaRepository
from app.personas.services import PersonaPageService, PersonaService


def get_persona_repository(db: Session = Depends(get_db)) -> PersonaRepository:
    return PersonaRepository(db=db)


def get_persona_service(
    repository: PersonaRepository = Depends(get_persona_repository),
) -> PersonaService:
    return PersonaService(persona_repository=repository)


def get_persona_page_service(
    persona_service: PersonaService = Depends(get_persona_service),
) -> PersonaPageService:
    return PersonaPageService(persona_service=persona_service)
