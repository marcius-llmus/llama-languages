from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine

from app.core.db import Base
from app.core.dependencies import get_db
from app.main import app

pytest_plugins = [
    "tests.personas.fixtures",
    "tests.language_profiles.fixtures",
    "tests.settings.fixtures",
    "tests.conversation.fixtures",
]

# Use an in-memory SQLite database for testing
engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)


@pytest.fixture(scope="session", autouse=True)
def setup_db() -> Generator[None, None, None]:
    """
    Create database tables before tests run, and drop them after.
    """
    # Import all models here so that SQLModel knows about them
    from app.language_profiles import models  # noqa
    from app.personas import models  # noqa
    from app.settings import models as settings_models  # noqa

    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Provides a transactional session for each test function, rolling back at the end."""
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.rollback()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Provides a TestClient with the database dependency overridden.
    """

    def get_db_override() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = get_db_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()