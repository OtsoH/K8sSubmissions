"""Run: uv run --project . test_broadcast.py  (from todo-backend/)"""

import os

os.environ["NATS_URL"] = "nats://127.0.0.1:4223"

from main import broadcast

broadcast("smoke test")
print("ok: broadcast swallows a dead NATS")
