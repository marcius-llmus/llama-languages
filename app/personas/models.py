from sqlalchemy import Column, Integer, String, Text
from app.core.db import Base


class Persona(Base):
    __tablename__ = "personas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    prompt = Column(Text, nullable=False)
