import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

LOG_FILE = Path(os.getenv("LOG_FILE", "/app/files/log.txt"))
COUNTER_FILE = Path(os.getenv("COUNTER_FILE", "/app/data/counter.txt"))

app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
def root():
    log_content = LOG_FILE.read_text() if LOG_FILE.exists() else "no log output yet\n"
    count = COUNTER_FILE.read_text().strip() if COUNTER_FILE.exists() else "0"
    return f"{log_content}Ping / Pongs: {count}"


def main():
    port = int(os.getenv("PORT", "3000"))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
