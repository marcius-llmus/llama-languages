from sqlalchemy import Column, Integer, String, Text

from app.core.db import Base


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, default=1)
    gemini_api_key = Column(String, nullable=True)
    elevenlabs_api_key = Column(String, nullable=True)
    voice_id = Column(String, nullable=True)
    evaluation_prompt = Column(Text, nullable=True)
