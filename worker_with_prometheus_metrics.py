

import asyncio
import json
import random
from redis.asyncio import Redis
from async_redis_pool import get_redis_client
from prometheus_client import start_http_server, Counter, Gauge
import aiorun

redis: Redis = get_redis_client()

# Prometheus metrics
job_success = Counter("job_success_total", "Total successful jobs")
job_failure = Counter("job_failure_total", "Total failed jobs")
queue_length = Gauge("job_queue_length", "Current queue length")

async def process_job(job_id: str):
    job_data = await redis.hgetall(job_id)

    if not job_data:
        print(f"Job {job_id} not found.")
        return

    job_data = {k: v for k, v in job_data.items()}
    print(f"Processing {job_id} with data {job_data}")

    try:
        # Simulate random failure
        if random.random() < 0.3:
            raise Exception("Simulated failure")

        await asyncio.sleep(2)  # simulate work
        job_data["status"] = "completed"
        job_success.inc()

    except Exception as e:
        print(f"Job {job_id} failed: {e}")
        retries = int(job_data.get("retries", 0)) + 1
        job_data["status"] = "failed"
        job_data["retries"] = str(retries)
        job_failure.inc()
        await redis.rpush("failed_jobs", job_id)

    await redis.hset(job_id, mapping=job_data)

async def job_loop():
    print("Async Worker started. Waiting for jobs...")
    while True:
        queue_len = await redis.llen("job_queue")
        queue_length.set(queue_len)

        if queue_len == 0:
            await asyncio.sleep(1)
            continue

        result = await redis.blpop("job_queue", timeout=5)
        if result:
            _, job_id = result
            await process_job(job_id)



async def main():
    start_http_server(8000)  # Prometheus endpoint
    await job_loop()

if __name__ == "__main__":
    aiorun.run(main())
