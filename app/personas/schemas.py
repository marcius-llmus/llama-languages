from pydantic import BaseModel


class PersonaBase(BaseModel):
    name: str
    prompt: str


class PersonaCreate(PersonaBase):
    pass


class PersonaUpdate(BaseModel):
    name: str | None = None
    prompt: str | None = None


class PersonaRead(PersonaBase):
    id: int

    model_config = {"from_attributes": True}
