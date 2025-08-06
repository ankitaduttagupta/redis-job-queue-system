import uuid
import time
import json
from redis_pool import get_redis_client

r = get_redis_client()

for i in range(5):
    job_id = f"job-{uuid.uuid4()}" #hash key
    job_data = {
        "file": f"image_{i}.png",
        "action": "process_image",
        "status": "queued",
        "retries": 0,
        "created_at": time.time()
    }

    #push only job_id to queue
    r.rpush("job_queue", job_id)

    #store job metadata in hash
    r.hset(job_id, mapping=job_data)

    print(f"Enqueued job: {job_id}")
    time.sleep(1)