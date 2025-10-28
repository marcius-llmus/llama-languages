from unittest.mock import MagicMock

from app.language_profiles.models import LanguageProfile, PracticeTopic
from app.language_profiles.schemas import (
    LanguageProfileCreate,
    LanguageProfileUpdate,
    PracticeTopicCreate,
)
from app.language_profiles.services import LanguageProfilePageService, LanguageProfileService
from app.personas.models import Persona


class TestLanguageProfileService:
    def test_get_language_profile(
        self,
        language_profile_service: LanguageProfileService,
        language_profile: LanguageProfile,
        language_profile_repository_mock: MagicMock,
    ):
        language_profile_repository_mock.get.return_value = language_profile
        result = language_profile_service.get_language_profile(profile_id=language_profile.id)
        language_profile_repository_mock.get.assert_called_once_with(
            pk=language_profile.id
        )
        assert result == language_profile

    def test_list_language_profiles(
        self,
        language_profile_service: LanguageProfileService,
        language_profile: LanguageProfile,
        language_profile_repository_mock: MagicMock,
    ):
        language_profile_repository_mock.list.return_value = [language_profile]
        result = language_profile_service.list_language_profiles()
        language_profile_repository_mock.list.assert_called_once()
        assert result == [language_profile]

    def test_create_language_profile(
        self,
        language_profile_service: LanguageProfileService,
        language_profile_repository_mock: MagicMock,
    ):
        profile_in = LanguageProfileCreate(
            name="New", target_language="German", persona_id=1
        )
        language_profile_service.create_language_profile(profile_in=profile_in)
        language_profile_repository_mock.create.assert_called_once_with(obj_in=profile_in)

    def test_update_language_profile(
        self,
        language_profile_service: LanguageProfileService,
        language_profile: LanguageProfile,
        language_profile_repository_mock: MagicMock,
    ):
        language_profile_repository_mock.get.return_value = language_profile
        profile_in = LanguageProfileUpdate(
            name="New", target_language="German", persona_id=1
        )

        language_profile_service.update_language_profile(profile_id=language_profile.id, profile_in=profile_in)

        language_profile_repository_mock.get.assert_called_once_with(pk=language_profile.id)
        language_profile_repository_mock.update.assert_called_once_with(
            db_obj=language_profile, obj_in=profile_in
        )

    def test_delete_language_profile(
        self,
        language_profile_service: LanguageProfileService,
        language_profile_repository_mock: MagicMock,
    ):
        language_profile_service.delete_language_profile(profile_id=1)
        language_profile_repository_mock.delete.assert_called_once_with(pk=1)

    def test_get_practice_topic_description_or_default(
        self,
        language_profile_service: LanguageProfileService,
        practice_topic: PracticeTopic,
        practice_topic_repository_mock: MagicMock,
    ):
        default_desc = "an open conversation"

        # Case 1: topic_id is None
        assert (
            language_profile_service.get_practice_topic_description_or_default(topic_id=None)
            == default_desc
        )

        # Case 2: Topic not found
        practice_topic_repository_mock.get.return_value = None
        assert (
            language_profile_service.get_practice_topic_description_or_default(topic_id=999)
            == default_desc
        )

        # Case 3: Topic found
        practice_topic_repository_mock.get.return_value = practice_topic
        assert (
            language_profile_service.get_practice_topic_description_or_default(topic_id=practice_topic.id)
            == practice_topic.name
        )

    def test_get_practice_topic(
        self,
        language_profile_service: LanguageProfileService,
        practice_topic: PracticeTopic,
        practice_topic_repository_mock: MagicMock,
    ):
        language_profile_service.get_practice_topic(topic_id=practice_topic.id)
        practice_topic_repository_mock.get.assert_called_once_with(pk=practice_topic.id)

    def test_add_topic_to_profile(
        self,
        language_profile_service: LanguageProfileService,
        practice_topic_repository_mock: MagicMock,
    ):
        topic_in = PracticeTopicCreate(name="New Topic")
        language_profile_service.add_topic_to_profile(profile_id=1, topic_in=topic_in)
        practice_topic_repository_mock.create_for_profile.assert_called_once_with(
            profile_id=1, obj_in=topic_in
        )

    def test_delete_topic(
        self,
        language_profile_service: LanguageProfileService,
        practice_topic_repository_mock: MagicMock,
    ):
        language_profile_service.delete_topic(topic_id=1)
        practice_topic_repository_mock.delete.assert_called_once_with(pk=1)


class TestLanguageProfilePageService:
    def test_get_language_profiles_page_data(
        self,
        language_profile_page_service: LanguageProfilePageService,
        language_profile_service_mock: MagicMock,
        persona_service_mock: MagicMock,
    ):
        language_profile_page_service.get_language_profiles_page_data()
        language_profile_service_mock.list_language_profiles.assert_called_once()
        persona_service_mock.list_personas.assert_called_once()

    def test_get_edit_language_profile_form_data(
        self,
        language_profile_page_service: LanguageProfilePageService,
        language_profile: LanguageProfile,
        persona: Persona,
        language_profile_service_mock: MagicMock,
        persona_service_mock: MagicMock,
    ):
        language_profile_service_mock.get_language_profile.return_value = language_profile
        persona_service_mock.list_personas.return_value = [persona]
        language_profile_page_service.get_edit_language_profile_form_data(
            profile_id=language_profile.id
        )
        language_profile_service_mock.get_language_profile.assert_called_once_with(
            language_profile.id
        )
        persona_service_mock.list_personas.assert_called_once()