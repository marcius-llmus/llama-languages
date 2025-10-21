from pydantic import BaseModel


class SettingsBase(BaseModel):
    gemini_api_key: str | None = None
    elevenlabs_api_key: str | None = None
    voice_id: str | None = None
    evaluation_prompt: str | None = None


class SettingsRead(SettingsBase):
    class Config:
        from_attributes = True


class SettingsUpdate(SettingsBase):
    pass
