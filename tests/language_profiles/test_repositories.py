from app.language_profiles.models import LanguageProfile, PracticeTopic
from app.language_profiles.repositories import (
    LanguageProfileRepository,
    PracticeTopicRepository,
)
from app.language_profiles.schemas import LanguageProfileCreate, LanguageProfileUpdate, PracticeTopicCreate
from app.personas.models import Persona

class TestLanguageProfileRepository:
    def test_create_language_profile(
        self, language_profile_repository: LanguageProfileRepository, persona: Persona
    ):
        profile_in = LanguageProfileCreate(
            name="New Profile", target_language="French", persona_id=persona.id
        )
        created = language_profile_repository.create(obj_in=profile_in)
        assert created.id is not None
        assert created.name == "New Profile"

    def test_get_language_profile(
        self,
        language_profile_repository: LanguageProfileRepository,
        language_profile: LanguageProfile,
    ):
        retrieved = language_profile_repository.get(pk=language_profile.id)
        assert retrieved is not None
        assert retrieved.id == language_profile.id

    def test_list_language_profiles(
        self,
        language_profile_repository: LanguageProfileRepository,
        language_profile: LanguageProfile,
    ):
        profiles = language_profile_repository.list()
        assert len(profiles) >= 1
        assert any(p.id == language_profile.id for p in profiles)

    def test_update_language_profile(
        self,
        language_profile_repository: LanguageProfileRepository,
        language_profile: LanguageProfile,
    ):
        update_data = LanguageProfileUpdate(name="Updated Name")
        updated = language_profile_repository.update(
            db_obj=language_profile, obj_in=update_data
        )
        assert updated.name == "Updated Name"

    def test_delete_language_profile(
        self,
        language_profile_repository: LanguageProfileRepository,
        language_profile: LanguageProfile,
    ):
        deleted = language_profile_repository.delete(pk=language_profile.id)
        assert deleted is not None
        assert language_profile_repository.get(pk=language_profile.id) is None


class TestPracticeTopicRepository:
    def test_create_for_profile(
        self,
        practice_topic_repository: PracticeTopicRepository,
        language_profile: LanguageProfile,
    ):
        topic_in = PracticeTopicCreate(name="New Topic")
        created = practice_topic_repository.create_for_profile(
            profile_id=language_profile.id, obj_in=topic_in
        )
        assert created.id is not None
        assert created.name == "New Topic"
        assert created.language_profile_id == language_profile.id

    def test_delete_topic(
        self,
        practice_topic_repository: PracticeTopicRepository,
        practice_topic: PracticeTopic,
    ):
        deleted = practice_topic_repository.delete(pk=practice_topic.id)
        assert deleted is not None
        assert practice_topic_repository.get(pk=practice_topic.id) is None