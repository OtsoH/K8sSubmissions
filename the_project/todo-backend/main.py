import os
import threading

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MAX_TODO_LENGTH = 140

app = FastAPI()

todos = [
    "Buy a car",
    "Get employed by Ericsson",
    "Plant a garden",
    "Make a new friend",
]
todos_lock = threading.Lock()


class NewTodo(BaseModel):
    todo: str = Field(min_length=1, max_length=MAX_TODO_LENGTH)


@app.get("/todos")
def get_todos():
    with todos_lock:
        return list(todos)


@app.post("/todos", status_code=201)
def create_todo(new_todo: NewTodo):
    text = new_todo.todo.strip()
    if not text:
        raise HTTPException(status_code=400, detail="todo must not be empty")
    with todos_lock:
        todos.append(text)
    print(f"Created todo: {text}", flush=True)
    return {"todo": text}


def main():
    port = int(os.getenv("PORT", "3000"))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
