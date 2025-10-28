from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    DATABASE_URL: str = "sqlite:///./database.db"
    AUDIO_OUTPUT_DIR: str = "app/static/audio"
    PERSONAS_SEED_PATH: str = "app/seed/personas.yaml"
    LANGUAGE_PROFILES_SEED_PATH: str = "app/seed/language_profiles.yaml"


settings = Settings()  # type: ignore
