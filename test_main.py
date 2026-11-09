from fastapi.testclient import TestClient

# fastapi app instance
from main import app

# test client instance
client = TestClient(app)

def test_get_todos():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == []

def test_create_todo():
    response = client.post("/todos", json={"description": "Test Todo"})
    assert response.status_code == 200
    assert response.json()["description"] == "Test Todo"
    assert response.json()["completed"] == False
    assert response.json()["created_at"] is not None

def test_get_todo():
    create_response = client.post("/todos", json={"description": "Test Todo"})
    response = client.get(f"/todos/{create_response.json()['id']}")
    assert response.status_code == 200
    assert response.json()["description"] == "Test Todo"
    assert response.json()["completed"] == False
    assert response.json()["created_at"] is not None

def test_update_todo():
    create_response = client.post("/todos", json={"description": "Test Todo"})
    response = client.put(f"/todos/{create_response.json()['id']}", json={"description": "Updated Test Todo", "completed": True})
    assert response.status_code == 200
    assert response.json()["description"] == "Updated Test Todo"
    assert response.json()["completed"] == True
    assert response.json()["created_at"] is not None

def test_delete_todo():
    create_response = client.post("/todos", json={"description": "Test Todo"})
    response = client.delete(f"/todos/{create_response.json()['id']}")
    assert response.status_code == 200
    assert response.json() == {"message": "Todo deleted successfully"}
    response = client.get(f"/todos/{create_response.json()['id']}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}