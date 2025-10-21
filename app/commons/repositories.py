from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.db import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    model: Type[ModelType]

    def __init__(self, db: Session):
        self.db = db

    def get(self, pk: Any) -> ModelType | None:
        return self.db.get(self.model, pk)

    def create(self, obj_in: BaseModel) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        self.db.add(db_obj)
        self.db.flush()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, *, db_obj: ModelType, obj_in: BaseModel) -> ModelType:
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_obj, key, value)
        self.db.add(db_obj)
        self.db.flush()
        self.db.refresh(db_obj)
        return db_obj

    def delete(self, *, pk: Any) -> ModelType | None:
        db_obj = self.db.get(self.model, pk)
        if db_obj:
            self.db.delete(db_obj)
            self.db.flush()
        return db_obj
