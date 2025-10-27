from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.db import Base


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, default=1)
    gemini_api_key = Column(String, nullable=True)
    elevenlabs_api_key = Column(String, nullable=True)
    voice_id = Column(String, nullable=True)
    evaluation_prompt = Column(Text, nullable=True)
    feedback_language = Column(String, nullable=True)

    transcription_settings_id = Column(Integer, ForeignKey("llm_settings.id"), nullable=False)
    persona_settings_id = Column(Integer, ForeignKey("llm_settings.id"), nullable=False)
    feedback_settings_id = Column(Integer, ForeignKey("llm_settings.id"), nullable=False)

    transcription_settings = relationship("LLMSettings", foreign_keys=[transcription_settings_id])
    persona_settings = relationship("LLMSettings", foreign_keys=[persona_settings_id])
    feedback_settings = relationship("LLMSettings", foreign_keys=[feedback_settings_id])


class LLMSettings(Base):
    __tablename__ = "llm_settings"

    id = Column(Integer, primary_key=True)
    model = Column(String, nullable=False)
    temperature = Column(Float, nullable=False)

    __table_args__ = (UniqueConstraint("model", "temperature", name="_model_temperature_uc"),)
