from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.db import Base


class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    prompt = Column(Text, nullable=False)

    language_profiles = relationship("LanguageProfile", back_populates="persona")
