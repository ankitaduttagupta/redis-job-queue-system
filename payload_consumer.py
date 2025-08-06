import time
from redis_pool import get_redis_client

r = get_redis_client()
MAX_RETRIES = 3

while True:
    job_id = r.lpop("job_queue")
    if not job_id:
        print("No jobs in queue. Sleeping...")
        time.sleep(2)
        continue

    job = r.hgetall(job_id)

    if not job:
        print(f"Job metadata not found for {job_id}")
        continue

    # Decode bytes to string
    job = {k.decode(): v.decode() for k, v in job.items()}
    print(f"Processing: {job_id} - {job}")

    try:
        # Simulate job processing
        if job["file"].endswith("2.png"):
            raise Exception("Simulated failure")

        # Mark job as completed
        r.hset(job_id, mapping={"status": "completed"})
        print(f"Success: {job_id}")

    except Exception as e:
        retries = int(job.get("retries", 0)) + 1
        if retries > MAX_RETRIES:
            # Move to dead-letter queue
            r.rpush("failed_jobs", job_id)
            r.hset(job_id, mapping={"status": "failed", "error": str(e)})
            print(f"Failed: {job_id} moved to DLQ")
        else:
            # Retry later
            r.rpush("job_queue", job_id)
            r.hset(job_id, mapping={"retries": retries, "status": "retrying"})
            print(f" Retrying: {job_id} (attempt {retries})")

    time.sleep(1)
