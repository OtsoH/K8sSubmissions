import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path(os.getenv("LOG_FILE", "/app/files/log.txt"))


def timestamp():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def main():
    random_string = str(uuid.uuid4())
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    while True:
        line = f'{timestamp()}: {random_string}'
        with LOG_FILE.open('a') as f:
            f.write(line + '\n')
        print(line, flush=True)
        time.sleep(5)


if __name__ == "__main__":
    main()
