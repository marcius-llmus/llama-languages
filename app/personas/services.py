from typing import Sequence

from app.personas.models import Persona
from app.personas.repositories import PersonaRepository
from app.personas.schemas import PersonaCreate, PersonaUpdate


class PersonaService:
    def __init__(self, persona_repository: PersonaRepository):
        self.persona_repository = persona_repository

    def get_persona(self, persona_id: int) -> Persona | None:
        return self.persona_repository.get(pk=persona_id)

    def list_personas(self) -> Sequence[Persona]:
        return self.persona_repository.list()

    def create_persona(self, *, persona_in: PersonaCreate) -> Persona:
        return self.persona_repository.create(obj_in=persona_in)

    def update_persona(self, *, persona_id: int, persona_in: PersonaUpdate) -> Persona | None:
        db_obj = self.get_persona(persona_id)
        if not db_obj:
            return None
        return self.persona_repository.update(db_obj=db_obj, obj_in=persona_in)

    def delete_persona(self, *, persona_id: int) -> Persona | None:
        return self.persona_repository.delete(pk=persona_id)


class PersonaPageService:
    def __init__(self, persona_service: PersonaService):
        self.persona_service = persona_service

    def get_personas_page_data(self) -> dict:
        return {"personas": self.persona_service.list_personas()}
