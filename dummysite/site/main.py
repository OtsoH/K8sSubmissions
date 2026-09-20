import os
from functools import lru_cache

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, PlainTextResponse

WEBSITE_URL = os.environ["WEBSITE_URL"]
USER_AGENT = "dummysite/1.0 (https://github.com/OtsoH/K8sSubmissions) httpx"

app = FastAPI()


@lru_cache(maxsize=1)
def page():
    response = httpx.get(
        WEBSITE_URL,
        follow_redirects=True,
        timeout=10,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    html = response.text
    base = f'<base href="{WEBSITE_URL}">'
    if "<head>" in html:
        return html.replace("<head>", f"<head>{base}", 1)
    return base + html


@app.get("/healthz", response_class=PlainTextResponse)
def healthz():
    return "ok"


@app.get("/{path:path}", response_class=HTMLResponse)
def root(path: str):
    return page()


def main():
    port = int(os.getenv("PORT", "3000"))
    print(f"Serving a copy of {WEBSITE_URL} on port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
