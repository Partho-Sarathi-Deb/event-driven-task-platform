import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from database import Base, get_db
import models
from main import app

# Set up SQLite in-memory engine
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

client = TestClient(app)

@patch("main.publish_event")
def test_create_task(mock_publish):
    # Pass JSON body instead of URL query parameters
    payload = {"title": "Test Task", "description": "Testing"}
    response = client.post("/tasks", json=payload)
    
    assert response.status_code == 200
    assert response.json()["title"] == "Test Task"
    assert "id" in response.json()
    mock_publish.assert_called_once()
