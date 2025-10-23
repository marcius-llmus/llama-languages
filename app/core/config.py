from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )
    DATABASE_URL: str
    GOOGLE_API_KEY: str
    ELEVENLABS_API_KEY: str
    AUDIO_OUTPUT_DIR: str = "static/audio"


settings = Settings()  # type: ignore
