from pydantic import BaseModel, Field
from app.commons.enums import GeminiModel


class LLMSettingsBase(BaseModel):
    model: GeminiModel
    temperature: float = Field(ge=0.0, le=1.0)


class LLMSettingsRead(LLMSettingsBase):
    model_config = {"from_attributes": True}


class LLMSettingsUpdate(LLMSettingsBase):
    pass

class LLMSettingsCreate(LLMSettingsBase):
    pass


class SettingsCreate(BaseModel):
    """Schema for creating the Settings object with foreign key IDs."""

    transcription_settings_id: int
    persona_settings_id: int
    feedback_settings_id: int
    gemini_api_key: str | None = None
    elevenlabs_api_key: str | None = None
    voice_id: str | None = None
    evaluation_prompt: str | None = None
    feedback_language: str | None = None


class SettingsBase(BaseModel):
    gemini_api_key: str | None = None
    elevenlabs_api_key: str | None = None
    voice_id: str | None = None
    evaluation_prompt: str | None = None
    feedback_language: str | None = None
    transcription_settings: LLMSettingsRead
    persona_settings: LLMSettingsRead
    feedback_settings: LLMSettingsRead

class SettingsRead(SettingsBase):
    model_config = {"from_attributes": True}


class SettingsUpdate(BaseModel):
    """Corrected schema for partial updates of Settings."""

    gemini_api_key: str | None = None
    elevenlabs_api_key: str | None = None
    voice_id: str | None = None
    evaluation_prompt: str | None = None
    feedback_language: str | None = None
    transcription_settings: LLMSettingsUpdate | None = Field(None, exclude=True)
    persona_settings: LLMSettingsUpdate | None = Field(None, exclude=True)
    feedback_settings: LLMSettingsUpdate | None = Field(None, exclude=True)
