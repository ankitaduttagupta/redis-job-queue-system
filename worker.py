# worker.py
import signal
import sys
import json
import time
from redis_pool import get_redis_client

QUEUE_NAME = "job_queue"
shutdown = False

def handle_shutdown(signum, frame):
    global shutdown
    print(f"\nReceived signal {signum}. Preparing to shut down...")
    shutdown = True

signal.signal(signal.SIGINT, handle_shutdown)   # Ctrl+C
signal.signal(signal.SIGTERM, handle_shutdown)  # docker stop, etc.

def process_job(job):
    print(f"  Processing job: {job['id']} with payload: {job['payload']}")
    time.sleep(2)  # Simulate processing time
    print(f"Done: {job['id']}")

def worker_loop():
    r = get_redis_client()
    print(" Worker started. Waiting for jobs...")

    while not shutdown:
        try:
            result = r.blpop(QUEUE_NAME, timeout=2)
            if result:
                _, job_data = result
                job = json.loads(job_data)
                process_job(job)
        except Exception as e:
            print(f" Error: {e}")
            time.sleep(1)

    print("Worker shutting down...")
    r.close()
    print("Shutdown complete.")

if __name__ == "__main__":
    worker_loop()
