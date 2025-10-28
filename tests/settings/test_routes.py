from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.commons.enums import GeminiModel
from app.settings.models import Settings
from app.settings.schemas import SettingsUpdate


class TestSettingsRoutes:
    def test_view_settings(
        self,
        client: TestClient,
        settings_page_service_mock: MagicMock,
        override_get_settings_page_service,
    ):
        settings_page_service_mock.get_settings_page_data.return_value = {
            "settings": Settings(id=1, feedback_language="English"),
            "GeminiModel": GeminiModel,
        }
        response = client.get("/settings/")
        assert response.status_code == 200
        assert "Settings" in response.text
        settings_page_service_mock.get_settings_page_data.assert_called_once()

    def test_handle_update_settings(
        self,
        client: TestClient,
        settings_service_mock: MagicMock,
        override_get_settings_service,
    ):
        settings_service_mock.update_settings.return_value = Settings(
            id=1, feedback_language="Spanish"
        )
        update_data = {"feedback_language": "Spanish"}

        response = client.post("/settings/", json=update_data, headers={"HX-Request": "true"})

        assert response.status_code == 200
        assert 'value="Spanish"' in response.text
        settings_service_mock.update_settings.assert_called_once()
        call_args = settings_service_mock.update_settings.call_args[1]
        assert "settings_in" in call_args
        assert isinstance(call_args["settings_in"], SettingsUpdate)
        assert call_args["settings_in"].feedback_language == "Spanish"