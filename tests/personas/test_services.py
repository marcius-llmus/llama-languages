from unittest.mock import MagicMock

from app.personas.models import Persona
from app.personas.schemas import PersonaCreate, PersonaUpdate
from app.personas.services import PersonaPageService, PersonaService


class TestPersonaService:
    def test_get_persona_found(self, persona_service: PersonaService, persona_repository_mock: MagicMock, persona: Persona):
        persona_repository_mock.get.return_value = persona

        result = persona_service.get_persona(persona_id=persona.id)

        persona_repository_mock.get.assert_called_once_with(pk=persona.id)
        assert result == persona

    def test_get_persona_not_found(self, persona_service: PersonaService, persona_repository_mock: MagicMock):
        persona_repository_mock.get.return_value = None

        result = persona_service.get_persona(persona_id=1)

        persona_repository_mock.get.assert_called_once_with(pk=1)
        assert result is None

    def test_list_personas(self, persona_service: PersonaService, persona_repository_mock: MagicMock, persona: Persona):
        persona_repository_mock.list.return_value = [persona]

        result = persona_service.list_personas()

        persona_repository_mock.list.assert_called_once()
        assert result == [persona]

    def test_create_persona(self, persona_service: PersonaService, persona_repository_mock: MagicMock):
        persona_in = PersonaCreate(name="New", prompt="New desc")

        persona_service.create_persona(persona_in=persona_in)

        persona_repository_mock.create.assert_called_once_with(obj_in=persona_in)

    def test_update_persona_found(self, persona_service: PersonaService, persona_repository_mock: MagicMock, persona: Persona):
        persona_in = PersonaUpdate(name="New")
        persona_repository_mock.get.return_value = persona

        persona_service.update_persona(persona_id=persona.id, persona_in=persona_in)

        persona_repository_mock.get.assert_called_once_with(pk=persona.id)
        persona_repository_mock.update.assert_called_once_with(
            db_obj=persona, obj_in=persona_in
        )

    def test_update_persona_not_found(self, persona_service: PersonaService, persona_repository_mock: MagicMock):
        persona_in = PersonaUpdate(name="New", prompt="New prompt")
        persona_repository_mock.get.return_value = None

        result = persona_service.update_persona(persona_id=1, persona_in=persona_in)

        persona_repository_mock.get.assert_called_once_with(pk=1)
        persona_repository_mock.update.assert_not_called()
        assert result is None

    def test_delete_persona(self, persona_service: PersonaService, persona_repository_mock: MagicMock):
        persona_service.delete_persona(persona_id=1)
        persona_repository_mock.delete.assert_called_once_with(pk=1)


class TestPersonaPageService:
    def test_get_personas_page_data(self, persona_page_service: PersonaPageService, persona_service_mock: MagicMock, persona: Persona):
        mock_personas = [persona]
        persona_service_mock.list_personas.return_value = mock_personas

        result = persona_page_service.get_personas_page_data()

        persona_service_mock.list_personas.assert_called_once()
        assert result == {"personas": mock_personas}
