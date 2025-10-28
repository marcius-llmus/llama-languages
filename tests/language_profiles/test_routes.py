from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.language_profiles.models import LanguageProfile, PracticeTopic
from app.language_profiles.schemas import LanguageProfileUpdate, PracticeTopicCreate
from app.personas.models import Persona


class TestLanguageProfileRoutes:
    def test_view_language_profiles(
        self,
        client: TestClient,
        language_profile_page_service_mock: MagicMock,
        override_get_language_profile_page_service,
    ):
        language_profile_page_service_mock.get_language_profiles_page_data.return_value = {
            "language_profiles": [],
            "personas": [],
        }
        response = client.get("/language-profiles/")
        assert response.status_code == 200
        assert "Language Profiles" in response.text

    def test_create_language_profile(
        self,
        client: TestClient,
        language_profile_service_mock: MagicMock,
        override_get_language_profile_service,
    ):
        mock_persona = Persona(id=1, name="Test Persona", prompt="p")
        language_profile_service_mock.create_language_profile.return_value = LanguageProfile(
            id=1, name="New Profile", target_language="Spanish", persona_id=1,
            persona=mock_persona,
            practice_topics=[]
        )
        form_data = {
            "name": "New Profile",
            "target_language": "Spanish",
            "persona_id": "1",
        }
        response = client.post(
            "/language-profiles/", data=form_data, headers={"HX-Request": "true"}
        )
        assert response.status_code == 200
        assert "New Profile" in response.text
        language_profile_service_mock.create_language_profile.assert_called_once()

    def test_delete_language_profile(
        self,
        client: TestClient,
        language_profile_service_mock: MagicMock,
        override_get_language_profile_service,
    ):
        response = client.delete("/language-profiles/1")
        assert response.status_code == 200
        language_profile_service_mock.delete_language_profile.assert_called_once_with(
            profile_id=1
        )

    def test_view_edit_language_profile_form(
        self,
        client: TestClient,
        language_profile_page_service_mock: MagicMock,
        override_get_language_profile_page_service,
    ):
        language_profile_page_service_mock.get_edit_language_profile_form_data.return_value = {
            "language_profile": LanguageProfile(id=1, name="Test Profile"),
            "personas": [Persona(id=1, name="Test Persona")],
        }
        response = client.get("/language-profiles/1/edit", headers={"HX-Request": "true"})
        assert response.status_code == 200
        assert 'value="Test Profile"' in response.text
        language_profile_page_service_mock.get_edit_language_profile_form_data.assert_called_once_with(
            profile_id=1
        )

    def test_update_language_profile(
        self,
        client: TestClient,
        language_profile_service_mock: MagicMock,
        override_get_language_profile_service,
    ):
        mock_persona = Persona(id=1, name="Test Persona", prompt="p")
        language_profile_service_mock.update_language_profile.return_value = LanguageProfile(
            id=1, name="Updated Profile", target_language="Spanish", persona_id=1,
            persona=mock_persona,
            practice_topics=[]
        )
        form_data = {"name": "Updated Profile", "target_language": "Spanish", "persona_id": 1}
        response = client.patch(
            "/language-profiles/1", data=form_data, headers={"HX-Request": "true"}
        )
        assert response.status_code == 200
        assert "Updated Profile" in response.text
        language_profile_service_mock.update_language_profile.assert_called_once()
        call_args = language_profile_service_mock.update_language_profile.call_args[1]
        assert call_args["profile_id"] == 1
        assert isinstance(call_args["profile_in"], LanguageProfileUpdate)

    def test_get_language_profile(
        self,
        client: TestClient,
        language_profile_service_mock: MagicMock,
        override_get_language_profile_service,
    ):
        mock_persona = Persona(id=1, name="Test Persona", prompt="p")
        language_profile_service_mock.get_language_profile.return_value = LanguageProfile(
            id=1, name="Test Profile", target_language="Spanish", persona_id=1,
            persona=mock_persona,
            practice_topics=[]
        )
        response = client.get("/language-profiles/1", headers={"HX-Request": "true"})
        assert response.status_code == 200
        assert "Test Profile" in response.text
        language_profile_service_mock.get_language_profile.assert_called_once_with(
            profile_id=1
        )


class TestPracticeTopicRoutes:
    def test_add_practice_topic(
        self,
        client: TestClient,
        language_profile_service_mock: MagicMock,
        override_get_language_profile_service,
    ):
        language_profile_service_mock.add_topic_to_profile.return_value = PracticeTopic(
            id=1, name="New Topic", language_profile_id=1
        )
        form_data = {"name": "New Topic"}
        response = client.post(
            "/language-profiles/1/topics", data=form_data, headers={"HX-Request": "true"}
        )
        assert response.status_code == 200
        assert "New Topic" in response.text
        language_profile_service_mock.add_topic_to_profile.assert_called_once()
        call_args = language_profile_service_mock.add_topic_to_profile.call_args[1]
        assert call_args["profile_id"] == 1
        assert isinstance(call_args["topic_in"], PracticeTopicCreate)

    def test_delete_practice_topic(
        self,
        client: TestClient,
        language_profile_service_mock: MagicMock,
        override_get_language_profile_service,
    ):
        response = client.delete("/language-profiles/topics/1")
        assert response.status_code == 200
        language_profile_service_mock.delete_topic.assert_called_once_with(topic_id=1)