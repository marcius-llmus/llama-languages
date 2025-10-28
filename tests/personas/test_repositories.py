from app.personas.models import Persona
from app.personas.repositories import PersonaRepository
from app.personas.schemas import PersonaCreate, PersonaUpdate

class TestPersonaRepository:
    def test_create_persona(self, persona_repository: PersonaRepository):
        persona_in = PersonaCreate(name="New Persona", prompt="A new prompt.")
        created_persona = persona_repository.create(obj_in=persona_in)
        assert created_persona.id is not None
        assert created_persona.name == "New Persona"

    def test_get_persona(
        self, persona_repository: PersonaRepository, persona: Persona
    ):
        retrieved_persona = persona_repository.get(pk=persona.id)
        assert retrieved_persona is not None
        assert retrieved_persona.id == persona.id

    def test_list_personas(
        self, persona_repository: PersonaRepository, persona: Persona
    ):
        personas = persona_repository.list()
        assert len(personas) >= 1
        assert any(p.id == persona.id for p in personas)

    def test_update_persona(
        self, persona_repository: PersonaRepository, persona: Persona
    ):
        update_data = PersonaUpdate(name="Updated Name", prompt="Updated prompt")
        updated_persona = persona_repository.update(
            db_obj=persona, obj_in=update_data
        )
        assert updated_persona.name == "Updated Name"

    def test_delete_persona(
        self, persona_repository: PersonaRepository, persona: Persona
    ):
        deleted_persona = persona_repository.delete(pk=persona.id)
        assert deleted_persona is not None
        assert persona_repository.get(pk=persona.id) is None