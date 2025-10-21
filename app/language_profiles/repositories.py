from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.commons.repositories import BaseRepository
from app.language_profiles.models import LanguageProfile, PracticeTopic
from app.language_profiles.schemas import PracticeTopicCreate


class LanguageProfileRepository(BaseRepository[LanguageProfile]):
    model = LanguageProfile

    def __init__(self, db):
        super().__init__(db)

    def list(self) -> Sequence[LanguageProfile]:
        return (
            self.db.execute(
                select(self.model)
                .options(selectinload(self.model.practice_topics))
                .order_by(self.model.id)
            )
            .scalars()
            .all()
        )


class PracticeTopicRepository(BaseRepository[PracticeTopic]):
    model = PracticeTopic

    def __init__(self, db):
        super().__init__(db)

    def create_for_profile(
        self, *, profile_id: int, obj_in: PracticeTopicCreate
    ) -> PracticeTopic:
        db_obj = self.model(**obj_in.model_dump(), language_profile_id=profile_id)
        self.db.add(db_obj)
        self.db.flush()
        self.db.refresh(db_obj)
        return db_obj
