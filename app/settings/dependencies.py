from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.language_profiles.dependencies import get_language_profile_service
from app.language_profiles.services import LanguageProfileService
from app.personas.dependencies import get_persona_service
from app.personas.services import PersonaService
from app.settings.repositories import LLMSettingsRepository, SettingsRepository
from app.settings.services import (
    LLMSettingsService,
    SettingsPageService,
    SettingsService,
)


def get_settings_repository(db: Session = Depends(get_db)) -> SettingsRepository:
    return SettingsRepository(db=db)


def get_llm_settings_repository(
    db: Session = Depends(get_db),
) -> LLMSettingsRepository:
    return LLMSettingsRepository(db=db)


def get_llm_settings_service(
    repository: LLMSettingsRepository = Depends(get_llm_settings_repository),
) -> LLMSettingsService:
    return LLMSettingsService(llm_settings_repository=repository)


def get_settings_service(
    repository: SettingsRepository = Depends(get_settings_repository),
    llm_settings_service: LLMSettingsService = Depends(get_llm_settings_service),
    persona_service: PersonaService = Depends(get_persona_service),
    language_profile_service: LanguageProfileService = Depends(
        get_language_profile_service
    ),
) -> SettingsService:
    return SettingsService(
        settings_repository=repository,
        llm_settings_service=llm_settings_service,
        persona_service=persona_service,
        language_profile_service=language_profile_service,
    )


def get_settings_page_service(
    settings_service: SettingsService = Depends(get_settings_service),
) -> SettingsPageService:
    return SettingsPageService(settings_service=settings_service)
