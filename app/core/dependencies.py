from sqlalchemy.orm import Session
from app.core.db import engine

def get_db():
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
