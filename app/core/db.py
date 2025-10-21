from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings


engine = create_engine(settings.DATABASE_URL)


class Base(DeclarativeBase):
    pass
