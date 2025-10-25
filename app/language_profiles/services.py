from typing import Sequence

from app.language_profiles.models import LanguageProfile, PracticeTopic
from app.language_profiles.repositories import (
    LanguageProfileRepository,
    PracticeTopicRepository,
)
from app.language_profiles.schemas import (
    LanguageProfileCreate,
    LanguageProfileUpdate,
    PracticeTopicCreate,
)


class LanguageProfileService:
    def __init__(
        self,
        language_profile_repository: LanguageProfileRepository,
        practice_topic_repository: PracticeTopicRepository,
    ):
        self.language_profile_repository = language_profile_repository
        self.practice_topic_repository = practice_topic_repository

    def get_language_profile(self, profile_id: int) -> LanguageProfile | None:
        return self.language_profile_repository.get(pk=profile_id)

    def list_language_profiles(self) -> Sequence[LanguageProfile]:
        return self.language_profile_repository.list()

    def create_language_profile(
        self, *, profile_in: LanguageProfileCreate
    ) -> LanguageProfile:
        return self.language_profile_repository.create(obj_in=profile_in)

    def update_language_profile(
        self, *, profile_id: int, profile_in: LanguageProfileUpdate
    ) -> LanguageProfile | None:
        db_obj = self.get_language_profile(profile_id)
        if not db_obj:
            return None
        return self.language_profile_repository.update(db_obj=db_obj, obj_in=profile_in)

    def delete_language_profile(self, *, profile_id: int) -> LanguageProfile | None:
        return self.language_profile_repository.delete(pk=profile_id)

    def get_practice_topic_description_or_default(self, *, topic_id: int | None) -> str:
        default_description = "an open conversation"
        if not topic_id:
            return default_description

        topic = self.get_practice_topic(topic_id=topic_id)
        if not topic:
            return default_description

        return topic.name

    def get_practice_topic(self, *, topic_id: int) -> PracticeTopic | None:
        return self.practice_topic_repository.get(pk=topic_id)

    def add_topic_to_profile(
        self, *, profile_id: int, topic_in: PracticeTopicCreate
    ) -> PracticeTopic:
        return self.practice_topic_repository.create_for_profile(
            profile_id=profile_id, obj_in=topic_in
        )

    def delete_topic(self, *, topic_id: int) -> PracticeTopic | None:
        return self.practice_topic_repository.delete(pk=topic_id)


class LanguageProfilePageService:
    def __init__(self, language_profile_service: LanguageProfileService):
        self.language_profile_service = language_profile_service

    def get_language_profiles_page_data(self) -> dict:
        return {
            "language_profiles": self.language_profile_service.list_language_profiles()
        }
