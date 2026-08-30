import os
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

LOG_FILE = Path(os.getenv("LOG_FILE", "/app/files/log.txt"))
PING_PONG_URL = os.getenv("PING_PONG_URL", "http://ping-pong-svc:3456/pings")
INFORMATION_FILE = Path(os.getenv("INFORMATION_FILE", "/app/config/information.txt"))
MESSAGE = os.getenv("MESSAGE", "no message set")

app = FastAPI()


def pong_count():
    try:
        response = httpx.get(PING_PONG_URL, timeout=2)
        response.raise_for_status()
        return response.text.strip()
    except httpx.HTTPError as exc:
        print(f"ping-pong unreachable: {exc}", flush=True)
        return "unavailable"


@app.get("/", response_class=PlainTextResponse)
def root():
    information = (
        INFORMATION_FILE.read_text().strip()
        if INFORMATION_FILE.exists()
        else "no information file"
    )
    log_content = LOG_FILE.read_text() if LOG_FILE.exists() else "no log output yet\n"
    return (
        f"file content: {information}\n"
        f"env variable: MESSAGE={MESSAGE}\n"
        f"{log_content}Ping / Pongs: {pong_count()}"
    )


def main():
    port = int(os.getenv("PORT", "3000"))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
