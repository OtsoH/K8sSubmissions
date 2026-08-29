import html
import os
import time
import urllib.request
from pathlib import Path

import httpx
import uvicorn
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

CACHE_DIR = Path(os.getenv("IMAGE_CACHE_DIR", "/app/files"))
IMAGE_FILE = CACHE_DIR / "image.jpg"
IMAGE_URL = "https://picsum.photos/1200"
CACHE_SECONDS = 600
MAX_TODO_LENGTH = 140
TODO_BACKEND_URL = os.getenv("TODO_BACKEND_URL", "http://todo-backend-svc:2346")

app = FastAPI()


def fetch_todos():
    try:
        response = httpx.get(f"{TODO_BACKEND_URL}/todos", timeout=2)
        response.raise_for_status()
        return response.json()
    except (httpx.HTTPError, ValueError) as error:
        print(f"todo-backend unreachable: {error}", flush=True)
        return None


def render_items(todos):
    if todos is None:
        return "    <li><em>todo-backend is unavailable</em></li>"
    if not todos:
        return "    <li><em>Nothing to do yet</em></li>"
    return "\n".join(f"    <li>{html.escape(todo)}</li>" for todo in todos)


def render_page(todos):
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Todo app</title>
  <style>
    body {{ font-family: sans-serif; margin: 2rem; }}
    h1 {{ margin: 0 0 1rem; }}
    img {{ max-width: 100%; height: auto; display: block; }}
    .new-todo {{ margin: 1rem 0; }}
    .new-todo input {{ width: 24rem; max-width: 100%; padding: 0.3rem; }}
    ul {{ padding-left: 1.25rem; }}
  </style>
</head>
<body>
  <h1>Todo app</h1>
  <img src="/image" alt="A random picture, refreshed every 10 minutes">
  <form class="new-todo" method="post" action="/todos">
    <input type="text" name="todo" maxlength="{MAX_TODO_LENGTH}" required
           placeholder="What needs doing?" aria-label="New todo">
    <button type="submit">Send</button>
  </form>
  <ul>
{render_items(todos)}
  </ul>
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
    return render_page(fetch_todos())


@app.post("/todos")
def create_todo(todo: str = Form(...)):
    text = todo.strip()[:MAX_TODO_LENGTH]
    if text:
        try:
            response = httpx.post(
                f"{TODO_BACKEND_URL}/todos", json={"todo": text}, timeout=2
            )
            response.raise_for_status()
        except httpx.HTTPError as error:
            print(f"Could not create todo: {error}", flush=True)
    return RedirectResponse("/", status_code=303)


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
