# worker_async.py

import asyncio
import signal
import time
import json
from redis_pool import get_redis_client

QUEUE_NAME = "job_queue"
FAILED_QUEUE = "failed_jobs"
MAX_RETRIES = 3
SHUTDOWN = False


async def process_job(job_id, job_data):
    # Simulate failure for even-numbered UUID chunks (for testing)
    if int(job_id.split("-")[-1], 16) % 2 == 0:
        raise Exception("Simulated failure")
    print(f"[WORKER] Successfully processed {job_id}")


async def handle_job(job_id):
    global r

    job_data = r.hgetall(job_id)
    if not job_data:
        print(f"[WORKER] No metadata found for job: {job_id}")
        return

    # Decode byte values from Redis hash
    job_data = {k.decode(): v.decode() for k, v in job_data.items()}
    retries = int(job_data.get("retries", 0))

    try:
        print(f"[WORKER] Processing {job_id} (Attempt {retries + 1})")
        await process_job(job_id, job_data)
        r.delete(job_id)  # Cleanup after success
    except Exception as e:
        print(f"[WORKER] Failed {job_id}: {e}")

        if retries < MAX_RETRIES:
            retries += 1
            r.hset(job_id, mapping={"retries": retries})
            backoff = 2 ** retries
            print(f"[WORKER] Retrying {job_id} in {backoff}s...")
            await asyncio.sleep(backoff)
            r.rpush(QUEUE_NAME, job_id)
        else:
            print(f"[WORKER] Moving {job_id} to {FAILED_QUEUE}")
            r.rpush(FAILED_QUEUE, job_id)


async def worker_loop():
    global r
    r = get_redis_client()
    print("[WORKER] Async worker started with Redis Hash metadata")

    while not SHUTDOWN:
        job_id = r.lpop(QUEUE_NAME)
        if job_id:
            job_id = job_id.decode()
            await handle_job(job_id)
        else:
            await asyncio.sleep(0.5)


def handle_shutdown(signum, frame):
    global SHUTDOWN
    print(f"[WORKER] Received shutdown signal ({signum})")
    SHUTDOWN = True


def main():
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        print("[WORKER] Graceful shutdown complete.")


if __name__ == "__main__":
    main()
