from pydantic import BaseModel


class PersonaBase(BaseModel):
    name: str
    prompt: str


class PersonaCreate(PersonaBase):
    pass


class PersonaUpdate(PersonaBase):
    pass


class PersonaRead(PersonaBase):
    id: int

    class Config:
        from_attributes = True
