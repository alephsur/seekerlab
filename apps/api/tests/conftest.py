import os

# Set before importing app modules. Never point the test client at local user data.
os.environ.update({
    "APP_ENV": "test", "DATABASE_URL": "sqlite+pysqlite:///:memory:",
    "DEV_AUTH_ENABLED": "true", "DEV_BUILDER_TOKEN": "b" * 48, "DEV_TESTER_TOKEN": "t" * 48,
})

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import create_engine, event  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402
from sqlalchemy.pool import StaticPool  # noqa: E402

from seekerlab.db import Base, get_session  # noqa: E402
from seekerlab.main import create_app  # noqa: E402


@pytest.fixture
def client():
    engine = create_engine("sqlite+pysqlite:///:memory:", poolclass=StaticPool,
                           connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def foreign_keys(connection, _):
        connection.execute("PRAGMA foreign_keys=ON")

    Base.metadata.create_all(engine)

    def override_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    app = create_app()
    app.dependency_overrides[get_session] = override_session
    with TestClient(app) as test_client:
        yield test_client
    engine.dispose()


@pytest.fixture
def builder_headers():
    return {"Authorization": "Bearer " + "b" * 48}


@pytest.fixture
def tester_headers():
    return {"Authorization": "Bearer " + "t" * 48}


@pytest.fixture
def campaign_payload():
    return {"title": "Test onboarding flow", "description": "Describe a usability problem in the onboarding flow.",
            "instructions": ["Open the application", "Describe a problem"],
            "reward_amount": "3.00", "currency": "USDC", "capacity": 1}
