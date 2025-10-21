from pydantic import BaseModel, ConfigDict


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


class LanguageProfileCreate(LanguageProfileBase):
    pass


class LanguageProfileUpdate(LanguageProfileBase):
    pass


class LanguageProfileRead(LanguageProfileBase):
    id: int
    practice_topics: list[PracticeTopicRead] = []
    model_config = ConfigDict(from_attributes=True)
