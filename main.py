from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
app = FastAPI()

class Todo(BaseModel):
    id: int
    description: str
    completed: bool = False
    created_at: datetime = datetime.now()

# list of todos JSON
todos = [
]

@app.get("/")
def read_root():
    return todos

@app.get("/todos/{item_id}")
def read_todo(item_id: int, q: str = None):
    return todos[item_id]

@app.post("/todos/")
def create_todo(item: Todo):
    todos.append(item.model_dump())
    return todos

@app.put("/todos/{item_id}")
def update_todo(item_id: int, item: Todo):
    todos[item_id] = item
    return todos[item_id]