from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from app.personas.models import Persona
from app.personas.schemas import PersonaCreate, PersonaUpdate

class TestPersonaRoutes:
    def test_view_personas(
        self,
        client: TestClient,
        persona_page_service_mock: MagicMock,
        override_get_persona_page_service,
    ):
        persona_page_service_mock.get_personas_page_data.return_value = {"personas": []}
        response = client.get("/personas/")
        assert response.status_code == 200
        assert "Personas" in response.text

    def test_create_persona(
        self, client: TestClient, persona_service_mock: MagicMock, override_get_persona_service
    ):
        persona_service_mock.create_persona.return_value = Persona(
            id=1, name="New Persona", prompt="A new prompt."
        )
        form_data = {"name": "New Persona", "prompt": "A new prompt."}

        response = client.post("/personas/", data=form_data, headers={"HX-Request": "true"})

        assert response.status_code == 200
        assert "New Persona" in response.text
        persona_service_mock.create_persona.assert_called_once()
        # Check that the argument is an instance of PersonaCreate
        call_args = persona_service_mock.create_persona.call_args[1]
        assert "persona_in" in call_args
        assert isinstance(call_args["persona_in"], PersonaCreate)
        assert call_args["persona_in"].name == "New Persona"

    def test_delete_persona(
        self, client: TestClient, persona_service_mock: MagicMock, override_get_persona_service
    ):
        response = client.delete("/personas/1")
        assert response.status_code == 200
        persona_service_mock.delete_persona.assert_called_once_with(persona_id=1)

    def test_view_edit_persona_form(
        self, client: TestClient, persona_service_mock: MagicMock, override_get_persona_service
    ):
        persona_service_mock.get_persona.return_value = Persona(
            id=1, name="Test Persona", prompt="A test prompt."
        )
        response = client.get("/personas/1/edit", headers={"HX-Request": "true"})
        assert response.status_code == 200
        assert 'value="Test Persona"' in response.text
        persona_service_mock.get_persona.assert_called_once_with(persona_id=1)

    def test_update_persona(
        self, client: TestClient, persona_service_mock: MagicMock, override_get_persona_service
    ):
        persona_service_mock.update_persona.return_value = Persona(
            id=1, name="Updated Persona", prompt="Updated prompt."
        )
        form_data = {"name": "Updated Persona", "prompt": "Updated prompt."}

        response = client.patch("/personas/1", data=form_data, headers={"HX-Request": "true"})

        assert response.status_code == 200
        assert "Updated Persona" in response.text
        call_args = persona_service_mock.update_persona.call_args[1]
        assert call_args["persona_id"] == 1
        assert isinstance(call_args["persona_in"], PersonaUpdate)
        assert call_args["persona_in"].name == "Updated Persona"

    def test_get_persona(
        self, client: TestClient, persona_service_mock: MagicMock, override_get_persona_service
    ):
        persona_service_mock.get_persona.return_value = Persona(
            id=1, name="Test Persona", prompt="A test prompt."
        )
        response = client.get("/personas/1", headers={"HX-Request": "true"})
        assert response.status_code == 200
        assert "Test Persona" in response.text
        persona_service_mock.get_persona.assert_called_once_with(persona_id=1)