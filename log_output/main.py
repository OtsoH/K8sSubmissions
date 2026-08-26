import os
import threading
import time
import uuid
from datetime import datetime, timezone

import uvicorn
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

random_string = str(uuid.uuid4())

app = FastAPI()


def log_output():
    while True:
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        print(f'{timestamp}: {random_string}', flush=True)
        time.sleep(5)

def req_current_status():
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    return f'{timestamp}: {random_string}'


@app.get("/", response_class=PlainTextResponse)
def root():
    return req_current_status()


def main():
    threading.Thread(target=log_output, daemon=True).start()

    port = int(os.getenv("PORT", "3000"))
    print(f"Server started in port {port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
