import os
import time
import urllib.request
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse

CACHE_DIR = Path(os.getenv("IMAGE_CACHE_DIR", "/app/files"))
IMAGE_FILE = CACHE_DIR / "image.jpg"
IMAGE_URL = "https://picsum.photos/1200"
CACHE_SECONDS = 600

app = FastAPI()

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Todo app</title>
  <style>
    body { font-family: sans-serif; margin: 2rem; }
    h1 { margin: 0 0 1rem; }
    img { max-width: 100%; height: auto; display: block; }
  </style>
</head>
<body>
  <h1>Todo app</h1>
  <img src="/image" alt="A random picture, refreshed every 10 minutes">
</body>
</html>
"""


def is_stale():
    if not IMAGE_FILE.exists():
        return True
    return time.time() - IMAGE_FILE.stat().st_mtime > CACHE_SECONDS


def fetch_image():
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = IMAGE_FILE.with_suffix(".tmp")
    with urllib.request.urlopen(IMAGE_URL, timeout=10) as response:
        tmp.write_bytes(response.read())
    tmp.replace(IMAGE_FILE)
    print(f"Cached a new image to {IMAGE_FILE}", flush=True)


@app.get("/", response_class=HTMLResponse)
def root():
    return PAGE


@app.get("/image")
def image():
    if is_stale():
        try:
            fetch_image()
        except Exception as error:
            print(f"Image fetch failed: {error}", flush=True)
            if not IMAGE_FILE.exists():
                raise HTTPException(status_code=503, detail="no image available")
            print("Serving the stale cached image instead", flush=True)
    return FileResponse(
        IMAGE_FILE,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-store"},
    )


def main():
    port = int(os.getenv("PORT", "3000"))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
