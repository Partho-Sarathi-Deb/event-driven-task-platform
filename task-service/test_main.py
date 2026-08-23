import json
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# 1. Test existing endpoint or docs route
def test_read_root():
    response = client.get("/tasks")
    assert response.status_code == 200

# 2. Validation error test (missing title)
def test_create_task_invalid_payload():
    response = client.post("/tasks", json={"description": "Missing title field"})
    assert response.status_code == 422  # Unprocessable Entity

# 3. Unit test with RabbitMQ mocked out
@patch("main.publish_event")
def test_create_task_success(mock_publish):
    payload = {"title": "Write unit tests", "description": "Cover core features with pytest"}
    response = client.post("/tasks", json=payload)
    
    assert response.status_code == 200 or response.status_code == 201
    assert response.json()["title"] == "Write unit tests"
    
    mock_publish.assert_called_once()
