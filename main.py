from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import random
import string

app = FastAPI()

class TodoCreate(BaseModel):
    description: str

class TodoUpdate(BaseModel):
    description: str
    completed: bool = False

class TodoResponse(BaseModel):
    id: str
    description: str
    completed: bool = False
    created_at: datetime = datetime.now()

todos: list[TodoResponse] = []

@app.get("/", response_model=list[TodoResponse])
def read_root() -> list[TodoResponse]:
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

@app.post("/todos", response_model=TodoResponse)
def create_todo(item: TodoCreate) -> TodoResponse:
    """
    Create a todo
    """
    # random id (5 alphanumeric characters)
    id = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    created_at = datetime.now()
    completed = False
    description = item.description.strip()

    todos.append(TodoResponse(id=id, description=description, completed=completed, created_at=created_at))
    return TodoResponse(id=id, description=description, completed=completed, created_at=created_at)

@app.put("/todos/{item_id}", response_model=TodoResponse)
def update_todo(item_id: str, item: TodoUpdate) -> TodoResponse:
    """
    Update a todo by id
    """
    for todo in todos:
        if todo.id == item_id:
            return TodoResponse(id=todo.id, description=item.description, completed=item.completed, created_at=todo.created_at)
    raise HTTPException(status_code=404, detail="Todo not found")

@app.delete("/todos/{item_id}", response_model=dict)
def delete_todo(item_id: str) -> dict:
    """
    Delete a todo by id
    """
    for todo in todos:
        if todo.id == item_id:
            todos.remove(todo)
            return {"message": "Todo deleted successfully"}
    raise HTTPException(status_code=404, detail="Todo not found")