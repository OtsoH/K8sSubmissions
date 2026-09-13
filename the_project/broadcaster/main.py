import asyncio
import os

import httpx
import nats

NATS_URL = os.getenv("NATS_URL", "nats://nats-svc:4222")
SUBJECT = "todos"


async def main():
    url = os.environ["BROADCAST_URL"]
    nc = await nats.connect(NATS_URL)
    print(f"Connected to {NATS_URL}, broadcasting to {url}", flush=True)

    async with httpx.AsyncClient(timeout=10) as client:

        async def handle(msg):
            text = msg.data.decode()
            response = await client.post(url, json={"user": "bot", "message": text})
            print(f"Broadcast ({response.status_code}): {text}", flush=True)

        await nc.subscribe(SUBJECT, queue="broadcaster", cb=handle)
        await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
