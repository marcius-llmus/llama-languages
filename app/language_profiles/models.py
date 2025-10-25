from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.db import Base


class LanguageProfile(Base):
    __tablename__ = "language_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    target_language = Column(String, nullable=False)
    persona_id = Column(Integer, ForeignKey("personas.id"), nullable=False, index=True)

    persona = relationship("Persona", back_populates="language_profiles")
    practice_topics = relationship(
        "PracticeTopic",
        back_populates="language_profile",
        cascade="all, delete-orphan",
    )


class PracticeTopic(Base):
    __tablename__ = "practice_topics"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    language_profile_id = Column(
        Integer, ForeignKey("language_profiles.id"), nullable=False
    )

    language_profile = relationship("LanguageProfile", back_populates="practice_topics")