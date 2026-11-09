from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import random
import string

class TodoCreate(BaseModel):
    description: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed: bool = False

app = FastAPI()

class TodoUpdate(BaseModel):
    description: str
    updated_at: datetime = Field(default_factory=datetime.now)
    completed: bool = False

class TodoResponse(BaseModel):
    id: str
    description: str
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

todos: list[TodoResponse] = []

@app.get("/todos", response_model=list[TodoResponse])
def read_todos() -> list[TodoResponse]:
    """
    Get all todos
    """
    return todos

@app.get("/todos/{item_id}", response_model=TodoResponse)
def read_todo(item_id: str) -> TodoResponse:
    """
    Get a todo by id
    """
    for todo in todos:
        if todo.id == item_id:
            return todo
    raise HTTPException(status_code=404, detail="Todo not found")

@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(item: TodoCreate) -> TodoResponse:
    """
    Create a todo
    """
    # random id (5 alphanumeric characters)
    id = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    todo = TodoResponse(
        id=id,
        description=item.description.strip(),
        completed=item.completed,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )
    todos.append(todo)
    return todo

@app.put("/todos/{item_id}", response_model=TodoResponse)
def update_todo(item_id: str, item: TodoUpdate) -> TodoResponse:
    """
    Update a todo by id
    """
    todo = read_todo(item_id)
    todo.description = item.description
    todo.completed = item.completed
    todo.updated_at = item.updated_at
    return todo

@app.delete("/todos/{item_id}", response_model=dict)
def delete_todo(item_id: str) -> dict:
    """
    Delete a todo by id
    """
    todo = read_todo(item_id)
    todos.remove(todo)
    return {"message": "Todo deleted successfully"}