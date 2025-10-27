from pydantic import BaseModel, ConfigDict

from app.personas.schemas import PersonaRead


# Practice Topic Schemas
class PracticeTopicBase(BaseModel):
    name: str


class PracticeTopicCreate(PracticeTopicBase):
    pass


class PracticeTopicRead(PracticeTopicBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# Language Profile Schemas
class LanguageProfileBase(BaseModel):
    name: str
    target_language: str
    persona_id: int


class LanguageProfileCreate(LanguageProfileBase):
    pass


class LanguageProfileUpdate(LanguageProfileBase):
    pass


class LanguageProfileRead(LanguageProfileBase):
    id: int
    practice_topics: list[PracticeTopicRead] = []
    persona: PersonaRead
    model_config = ConfigDict(from_attributes=True)