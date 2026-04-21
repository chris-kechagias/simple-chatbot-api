"""
Defines pytest fixtures for testing the FastAPI app, including a test database session and a TestClient with overridden dependencies.
"""

from contextlib import asynccontextmanager

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core import get_session
from main import app

engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)


@pytest.fixture(name="session")
def session_fixture():
    # Create tables, yield session, drop tables
    with Session(engine) as session:
        SQLModel.metadata.drop_all(engine)
        SQLModel.metadata.create_all(engine)
        yield session
        SQLModel.metadata.drop_all(engine)


@asynccontextmanager
async def lifespan_override(app):
    yield


@pytest.fixture(name="client")
def client_fixture(session):
    # override dependency, yield TestClient, clear override
    app.dependency_overrides[get_session] = lambda: session
    app.router.lifespan_context = lifespan_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
