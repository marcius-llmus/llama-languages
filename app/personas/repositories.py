from typing import Sequence

from sqlalchemy import select

from app.commons.repositories import BaseRepository
from app.personas.models import Persona


class PersonaRepository(BaseRepository[Persona]):
    model = Persona

    def __init__(self, db):
        super().__init__(db)

    def list(self) -> Sequence[Persona]:
        return self.db.execute(select(self.model).order_by(self.model.id)).scalars().all()
