import os
import threading

import uvicorn
from fastapi import FastAPI
from pathlib import Path
from fastapi.responses import PlainTextResponse

app = FastAPI()

counter = 0
counter_lock = threading.Lock()

COUNTER_FILE = Path(os.getenv("COUNTER_FILE", "/app/data/counter.txt"))

def next_count():
    with counter_lock:
        if COUNTER_FILE.exists():
            current = int(COUNTER_FILE.read_text().strip())
        else:
            current = 0
        COUNTER_FILE.write_text(str(current + 1))
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
