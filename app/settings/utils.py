import logging
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from app.core.config import settings
from app.language_profiles.schemas import LanguageProfileCreate, PracticeTopicCreate
from app.personas.schemas import PersonaCreate

logger = logging.getLogger(__name__)


def seed_initial_data(
    persona_service,
    language_profile_service,
):
    """Seeds the database with initial data from YAML files."""
    logger.info("No settings found. Seeding initial database...")

    # 1. Seed Personas
    personas_path = Path(settings.PERSONAS_SEED_PATH)
    if not personas_path.exists():
        logger.warning("personas.yaml not found. Skipping persona seeding.")
        return

    with open(personas_path, "r", encoding="utf-8") as f:
        personas_data = yaml.safe_load(f)

    created_personas = {}
    logger.info(f"Seeding {len(personas_data)} personas...")
    for persona_data in personas_data:
        persona_in = PersonaCreate(**persona_data)
        persona = persona_service.create_persona(persona_in=persona_in)
        created_personas[persona.name] = persona

    # 2. Seed Language Profiles and their Topics
    profiles_path = Path(settings.LANGUAGE_PROFILES_SEED_PATH)
    if not profiles_path.exists():
        logger.warning(
            "language_profiles.yaml not found. Skipping language profile seeding."
        )
        return

    with open(profiles_path, "r", encoding="utf-8") as f:
        profiles_data = yaml.safe_load(f)

    logger.info(f"Seeding {len(profiles_data)} language profiles...")
    for profile_data in profiles_data:
        persona_name = profile_data.pop("persona_name")
        practice_topics_data = profile_data.pop("practice_topics")

        persona = created_personas.get(persona_name)
        if not persona:
            logger.warning(
                f"Persona '{persona_name}' not found for profile '{profile_data['name']}'. Skipping."
            )
            continue

        profile_in = LanguageProfileCreate(persona_id=persona.id, **profile_data)
        profile = language_profile_service.create_language_profile(
            profile_in=profile_in
        )

        for topic_data in practice_topics_data:
            combined_name = f"{topic_data['name']} ({topic_data['difficulty'].capitalize()})"
            topic_in = PracticeTopicCreate(name=combined_name)
            language_profile_service.add_topic_to_profile(
                profile_id=profile.id, topic_in=topic_in
            )
    logger.info("Database seeding complete.")


def initialize_application_settings(db: Session) -> None:
    """
    Checks if application settings exist. If not, seeds the database with initial data
    and creates default settings. This should be called once at application startup.
    """
    from app.settings.repositories import SettingsRepository, LLMSettingsRepository
    from app.personas.repositories import PersonaRepository
    from app.personas.services import PersonaService
    from app.language_profiles.repositories import LanguageProfileRepository, PracticeTopicRepository
    from app.language_profiles.services import LanguageProfileService
    from app.commons.enums import GeminiModel
    from app.settings.schemas import LLMSettingsCreate, SettingsCreate
    from app.settings.services import LLMSettingsService

    settings_repository = SettingsRepository(db=db)
    existing_settings = settings_repository.get(pk=1)

    if existing_settings:
        logger.info("Application settings already initialized.")
        return

    logger.info("Initializing application settings...")

    llm_settings_repository = LLMSettingsRepository(db=db)
    llm_settings_service = LLMSettingsService(llm_settings_repository=llm_settings_repository)
    persona_service = PersonaService(persona_repository=PersonaRepository(db=db))
    language_profile_service = LanguageProfileService(
        language_profile_repository=LanguageProfileRepository(db=db),
        practice_topic_repository=PracticeTopicRepository(db=db),
    )

    seed_initial_data(
        persona_service=persona_service,
        language_profile_service=language_profile_service,
    )

    transcription_settings = llm_settings_service.get_or_create(
        llm_settings_id=None,
        settings_in=LLMSettingsCreate(
            model=GeminiModel.GEMINI_2_5_FLASH, temperature=0.0
        ),
    )
    persona_settings = llm_settings_service.get_or_create(
        llm_settings_id=None,
        settings_in=LLMSettingsCreate(
            model=GeminiModel.GEMINI_2_5_FLASH, temperature=0.7
        ),
    )
    feedback_settings = llm_settings_service.get_or_create(
        llm_settings_id=None,
        settings_in=LLMSettingsCreate(
            model=GeminiModel.GEMINI_2_5_FLASH, temperature=0.5
        ),
    )

    settings_in = SettingsCreate(
        transcription_settings_id=transcription_settings.id,
        persona_settings_id=persona_settings.id,
        feedback_settings_id=feedback_settings.id,
    )
    settings_repository.create(obj_in=settings_in)
    db.commit()

    logger.info("Application settings initialized successfully.")
