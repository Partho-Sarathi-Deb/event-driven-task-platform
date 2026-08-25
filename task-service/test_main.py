import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_task():
    response = client.post("/tasks/", json={"title": "Test Task", "description": "Test Description"})
    assert response.status_code in [200, 201]
    data = response.json()
    assert data["title"] == "Test Task"
    assert "id" in data

def test_get_all_tasks():
    response = client.get("/tasks/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_task_by_id_success():
    create_res = client.post("/tasks/", json={"title": "Fetch Me", "description": "To be fetched"})
    task_id = create_res.json()["id"]

    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Fetch Me"

def test_get_task_by_id_not_found():
    response = client.get("/tasks/999999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

def test_update_task_success():
    create_res = client.post("/tasks/", json={"title": "Old Title", "description": "Old Desc"})
    task_id = create_res.json()["id"]

    response = client.put(f"/tasks/{task_id}", json={"title": "New Title", "description": "Updated Desc"})
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

def test_update_task_not_found():
    response = client.put("/tasks/999999", json={"title": "Ghost Task", "description": "Does not exist"})
    assert response.status_code == 404

def test_delete_task_success():
    create_res = client.post("/tasks/", json={"title": "Delete Me", "description": "To be deleted"})
    task_id = create_res.json()["id"]

    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code in [200, 204]

    get_res = client.get(f"/tasks/{task_id}")
    assert get_res.status_code == 404

def test_delete_task_not_found():
    response = client.delete("/tasks/999999")
    assert response.status_code == 404
