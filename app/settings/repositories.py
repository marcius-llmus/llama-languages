from app.commons.repositories import BaseRepository
from app.settings.models import Settings
from app.settings.schemas import SettingsUpdate


class SettingsRepository(BaseRepository[Settings]):
    model = Settings

    def __init__(self, db):
        super().__init__(db)

    def get(self, pk: int = 1) -> Settings | None:
        return self.db.get(self.model, pk)

    def create(self, obj_in: SettingsUpdate) -> Settings:
        db_obj = self.model(**obj_in.model_dump(), id=1) # because it is only for local, lets hard code!!
        self.db.add(db_obj)
        self.db.flush()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, *, pk: int = 1) -> Settings | None:
        # This is a singleton model, it should not be deleted.
        raise NotImplementedError("You should not be calling it lol")
