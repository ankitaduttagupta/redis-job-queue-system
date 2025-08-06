
from redis_pool import get_redis_client

r = get_redis_client()

def get_failed_jobs():

    failed_job_ids = r.lrange("failed_jobs", 0, -1)
    failed_jobs = []

    for job_id in failed_job_ids:
        job_data = r.hgetall(job_id)
        if job_data:
            job_data["job_id"] = job_id  
            failed_jobs.append(job_data)

    return {"failed_jobs": failed_jobs}

if __name__ == "__main__":
    failed_jobs = get_failed_jobs()
    if failed_jobs["failed_jobs"]:
        print("Failed Jobs:")
        for job in failed_jobs["failed_jobs"]:
            print(f"Job ID: {job['job_id']}, Data: {job}")
    else:
        print("No failed jobs found.")



