import os
import time

import psycopg
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MAX_TODO_LENGTH = 140

app = FastAPI()


def wait_for_db():
    for _ in range(60):
        try:
            with psycopg.connect() as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS todos ("
                    "id serial PRIMARY KEY, "
                    f"content varchar({MAX_TODO_LENGTH}) NOT NULL)"
                )
            return
        except psycopg.OperationalError as e:
            print(f"Waiting for database: {e}", flush=True)
            time.sleep(2)
    raise RuntimeError("Database never became available")


class NewTodo(BaseModel):
    todo: str


@app.get("/todos")
def get_todos():
    with psycopg.connect() as conn:
        return [row[0] for row in conn.execute("SELECT content FROM todos ORDER BY id")]


@app.post("/todos", status_code=201)
def create_todo(new_todo: NewTodo):
    text = new_todo.todo.strip()
    if not text:
        print("Rejected todo: empty", flush=True)
        raise HTTPException(status_code=400, detail="todo must not be empty")
    if len(text) > MAX_TODO_LENGTH:
        print(f"Rejected todo: {len(text)} chars, max {MAX_TODO_LENGTH}: {text[:80]}...", flush=True)
        raise HTTPException(
            status_code=400, detail=f"todo must be at most {MAX_TODO_LENGTH} characters"
        )
    with psycopg.connect() as conn:
        conn.execute("INSERT INTO todos (content) VALUES (%s)", (text,))
    print(f"Created todo: {text}", flush=True)
    return {"todo": text}


def main():
    wait_for_db()
    port = int(os.getenv("PORT", "3000"))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
