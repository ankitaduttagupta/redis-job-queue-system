import json
import time
from redis_pool import get_redis_client

QUEUE_NAME = "job_queue"

def process(job):
    print(f"Processing job: {job['id']} with payload {job['payload']}")
    time.sleep(1)

def consume_jobs():
    r = get_redis_client()
    while True:
        _, job_data = r.blpop(QUEUE_NAME)
        job = json.loads(job_data)
        try:
            process(job)
        except Exception as e:
            print(f"Job failed: {job['id']} | Error: {e}")
            # Optionally requeue: r.rpush(QUEUE_NAME, job_data)

if __name__ == "__main__":
    consume_jobs()
