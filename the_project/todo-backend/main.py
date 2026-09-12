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
                conn.execute(
                    "ALTER TABLE todos "
                    "ADD COLUMN IF NOT EXISTS done boolean NOT NULL DEFAULT false"
                )
            return
        except psycopg.OperationalError as e:
            print(f"Waiting for database: {e}", flush=True)
            time.sleep(2)
    raise RuntimeError("Database never became available")


class NewTodo(BaseModel):
    todo: str


@app.get("/healthz")
def healthz():
    try:
        with psycopg.connect() as conn:
            conn.execute("SELECT 1")
    except psycopg.Error as error:
        print(f"Health check failed: {error}", flush=True)
        raise HTTPException(status_code=500, detail="database unavailable")
    return {"status": "ok"}


@app.get("/todos")
def get_todos():
    with psycopg.connect() as conn:
        rows = conn.execute("SELECT id, content, done FROM todos ORDER BY id")
        return [{"id": i, "content": content, "done": done} for i, content, done in rows]


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


@app.put("/todos/{todo_id}")
def mark_done(todo_id: int):
    with psycopg.connect() as conn:
        row = conn.execute(
            "UPDATE todos SET done = true WHERE id = %s RETURNING content", (todo_id,)
        ).fetchone()
    if row is None:
        print(f"Rejected done: no todo with id {todo_id}", flush=True)
        raise HTTPException(status_code=404, detail="todo not found")
    print(f"Marked done: {row[0]}", flush=True)
    return {"id": todo_id, "done": True}


def main():
    wait_for_db()
    port = int(os.getenv("PORT", "3000"))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
