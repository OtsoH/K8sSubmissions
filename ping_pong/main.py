import os
import threading

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI()

counter = 0
counter_lock = threading.Lock()


def next_count():
    global counter
    with counter_lock:
        current = counter
        counter += 1
    return current


@app.get("/", response_class=PlainTextResponse)
@app.get("/pingpong", response_class=PlainTextResponse)
def pingpong():
    return f"pong {next_count()}"


def main():
    port = int(os.getenv("PORT", "3000"))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
