import time
import uuid
from datetime import datetime, timezone


def log_output():
    random_string = str(uuid.uuid4())

    while True:
        timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        print(f'{timestamp}: {random_string}', flush=True)
        time.sleep(5)


if __name__ == "__main__":
    log_output()
