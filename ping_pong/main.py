import os
import time

import psycopg
import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

def query(sql):
    with psycopg.connect() as conn:
        return conn.execute(sql).fetchone()[0]


def wait_for_db():
    for _ in range(60):
        try:
            with psycopg.connect() as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS counter (id int PRIMARY KEY, value int NOT NULL)"
                )
                conn.execute("INSERT INTO counter VALUES (1, 0) ON CONFLICT DO NOTHING")
            return
        except psycopg.OperationalError as e:
            print(f"Waiting for database: {e}", flush=True)
            time.sleep(2)
    raise RuntimeError("Database never became available")


@app.get("/", response_class=PlainTextResponse)
@app.get("/pingpong", response_class=PlainTextResponse)
def pingpong():
    count = query("UPDATE counter SET value = value + 1 WHERE id = 1 RETURNING value - 1")
    return f"pong {count}"

@app.get("/pings", response_class=PlainTextResponse)
def pings():
    return str(query("SELECT value FROM counter WHERE id = 1"))

def main():
    wait_for_db()
    port = int(os.getenv("PORT", "3000"))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
