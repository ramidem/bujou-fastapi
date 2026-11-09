# --- imports ---
# datetime helpers for timestamp checks; UUID to validate id shape
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

# import the module (for clearing todos) and the FastAPI app under test
import main
from main import app

# shared HTTP client for all tests (in-process, no real server)
client = TestClient(app)

# fixed id that should never exist in an empty store
MISSING_ID = "00000000-0000-0000-0000-000000000000"


# --- fixtures / helpers ---

@pytest.fixture(autouse=True)
def clear_todos():
    # runs before every test so shared main.todos cannot leak across cases
    main.todos.clear()
    yield
    main.todos.clear()


def create_todo(description: str = "Test Todo", completed: bool = False) -> dict:
    # helper: create a todo and return the JSON body (fails if create is not 201)
    response = client.post(
        "/todos",
        json={"description": description, "completed": completed},
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def todo() -> dict:
    # per-test sample todo for get/update/delete happy paths
    return create_todo()


def parse_utc_datetime(value: str) -> datetime:
    # parse API timestamp; require timezone and UTC offset (not naive / local-only)
    parsed = datetime.fromisoformat(value)
    assert parsed.tzinfo is not None
    assert parsed.utcoffset() == timedelta(0)
    return parsed.astimezone(timezone.utc)


# --- list ---

def test_get_todos_empty():
    # empty store → empty list (only reliable because clear_todos runs first)
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []


# --- create ---

def test_create_todo():
    # happy path: fields, uuid4 id, timezone-aware timestamps
    body = create_todo("Test Todo")
    assert body["description"] == "Test Todo"
    assert body["completed"] is False
    assert UUID(body["id"]).version == 4
    parse_utc_datetime(body["created_at"])
    parse_utc_datetime(body["updated_at"])


@pytest.mark.parametrize("description", ["", "   "])
def test_create_todo_rejects_blank_description(description):
    # empty or whitespace-only description must fail validation (422)
    response = client.post("/todos", json={"description": description})
    assert response.status_code == 422


def test_create_todo_rejects_description_longer_than_100():
    # over max_length=100 must fail validation (422)
    response = client.post("/todos", json={"description": "a" * 101})
    assert response.status_code == 422


def test_create_todo_strips_description():
    # leading/trailing spaces are stripped before save
    body = create_todo("  hi  ")
    assert body["description"] == "hi"


def test_list_todos_contains_created_item():
    # create then list: the new item must show up in GET /todos
    created = create_todo("Listed Todo")
    response = client.get("/todos")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == created["id"]
    assert body[0]["description"] == "Listed Todo"
    assert body[0]["completed"] is False


# --- get by id ---

def test_get_todo(todo):
    # fetch the fixture todo by id and check payload
    response = client.get(f"/todos/{todo['id']}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == todo["id"]
    assert body["description"] == "Test Todo"
    assert body["completed"] is False
    parse_utc_datetime(body["created_at"])
    parse_utc_datetime(body["updated_at"])


def test_get_missing_todo_returns_404():
    # unknown id → 404 with FastAPI detail shape
    response = client.get(f"/todos/{MISSING_ID}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}


# --- update ---

def test_update_todo(todo):
    # change description/completed; updated_at must not go backwards; re-GET proves store
    prior_updated_at = parse_utc_datetime(todo["updated_at"])
    response = client.put(
        f"/todos/{todo['id']}",
        json={"description": "Updated Test Todo", "completed": True},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == todo["id"]
    assert body["description"] == "Updated Test Todo"
    assert body["completed"] is True
    parse_utc_datetime(body["created_at"])
    updated_at = parse_utc_datetime(body["updated_at"])
    assert updated_at >= prior_updated_at

    fetched = client.get(f"/todos/{todo['id']}")
    assert fetched.status_code == 200
    stored = fetched.json()
    assert stored["description"] == "Updated Test Todo"
    assert stored["completed"] is True
    assert stored["updated_at"] == body["updated_at"]


def test_update_missing_todo_returns_404():
    # put on unknown id → 404
    response = client.put(
        f"/todos/{MISSING_ID}",
        json={"description": "Missing", "completed": False},
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}


# --- delete ---

def test_delete_todo(todo):
    # delete succeeds, then get of same id is 404
    response = client.delete(f"/todos/{todo['id']}")
    assert response.status_code == 200
    assert response.json() == {"message": "Todo deleted successfully"}
    follow_up = client.get(f"/todos/{todo['id']}")
    assert follow_up.status_code == 404
    assert follow_up.json() == {"detail": "Todo not found"}


def test_delete_missing_todo_returns_404():
    # delete unknown id → 404
    response = client.delete(f"/todos/{MISSING_ID}")
    assert response.status_code == 404
    assert response.json() == {"detail": "Todo not found"}
