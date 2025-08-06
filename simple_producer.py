import json
import time
from redis_pool import get_redis_client

QUEUE_NAME = "job_queue"

def enqueue_job(job_id, payload):
    job = {
        "id": job_id,
        "payload": payload,
        "timestamp": time.time()
    }
    r = get_redis_client()
    r.rpush(QUEUE_NAME, json.dumps(job))
    print(f"Enqueued job: {job_id}")

if __name__ == "__main__":
    for i in range(5):
        enqueue_job(f"job-{i}", {"data": f"value-{i}"})
