import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

LOG_FILE = Path(os.getenv("LOG_FILE", "/app/files/log.txt"))

app = FastAPI()


@app.get("/", response_class=PlainTextResponse)
def root():
    if not LOG_FILE.exists():
        return "no log output yet"
    return LOG_FILE.read_text()


def main():
    port = int(os.getenv("PORT", "3000"))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
