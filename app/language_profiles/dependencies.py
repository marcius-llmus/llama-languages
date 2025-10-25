from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.language_profiles.repositories import (
    LanguageProfileRepository,
    PracticeTopicRepository,
)
from app.language_profiles.services import LanguageProfilePageService, LanguageProfileService
from app.personas.dependencies import get_persona_service
from app.personas.services import PersonaService


def get_language_profile_repository(
    db: Session = Depends(get_db),
) -> LanguageProfileRepository:
    return LanguageProfileRepository(db=db)


def get_practice_topic_repository(db: Session = Depends(get_db)) -> PracticeTopicRepository:
    return PracticeTopicRepository(db=db)


def get_language_profile_service(
    language_profile_repository: LanguageProfileRepository = Depends(
        get_language_profile_repository
    ),
    practice_topic_repository: PracticeTopicRepository = Depends(
        get_practice_topic_repository
    ),
) -> LanguageProfileService:
    return LanguageProfileService(
        language_profile_repository=language_profile_repository,
        practice_topic_repository=practice_topic_repository,
    )


def get_language_profile_page_service(
    language_profile_service: LanguageProfileService = Depends(get_language_profile_service),
    persona_service: PersonaService = Depends(get_persona_service),
) -> LanguageProfilePageService:
    return LanguageProfilePageService(
        language_profile_service=language_profile_service,
        persona_service=persona_service,
    )