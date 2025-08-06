# Redis Job Queue System

This POC demonstrates a lightweight custom job queue using Redis as the backend.

- Enqueue/dequeue jobs using Redis Lists
- Connection pooling via `redis-py`
- Simple retry hooks
- Blocking queue consumption (`BLPOP`)
- Redis async worker is running
- Prometheus metrics are exposed on localhost:8000
- Prometheus server is scraping metrics from your worker
- View real-time metrics (job_success_total, job_failure_total,
  job_queue_length) in the Prometheus dashboard localhost:9090

## How to Run

###  Start Redis via Docker
```bash
docker run -p 6379:6379 redis
```
to check the redis is working , execute the redis in docker:
```bash
docker exec -it <ur container> redis-cli ping
```
```bash
(.venv) ankitaduttagupta@ANKITAs-MacBook-Air redis-job-queue-system % python3 producer.py 
Enqueued job: job-0
Enqueued job: job-1
Enqueued job: job-2
Enqueued job: job-3
Enqueued job: job-4
(.venv) ankitaduttagupta@ANKITAs-MacBook-Air redis-job-queue-system % docker exec -it thirsty_keller redis-cli

127.0.0.1:6379> keys *
1) "job_queue"
127.0.0.1:6379> LRANGE job_queue 0 -1
1) "{\"id\": \"job-0\", \"payload\": {\"data\": \"value-0\"}, \"timestamp\": 1754460163.146245}"
2) "{\"id\": \"job-1\", \"payload\": {\"data\": \"value-1\"}, \"timestamp\": 1754460163.156137}"
3) "{\"id\": \"job-2\", \"payload\": {\"data\": \"value-2\"}, \"timestamp\": 1754460163.1586912}"
4) "{\"id\": \"job-3\", \"payload\": {\"data\": \"value-3\"}, \"timestamp\": 1754460163.161271}"
5) "{\"id\": \"job-4\", \"payload\": {\"data\": \"value-4\"}, \"timestamp\": 1754460163.1645608}"

(.venv) ankitaduttagupta@ANKITAs-MacBook-Air redis-job-queue-system % python3 consumer.py 
Processing job: job-0 with payload {'data': 'value-0'}
Processing job: job-1 with payload {'data': 'value-1'}
Processing job: job-2 with payload {'data': 'value-2'}
Processing job: job-3 with payload {'data': 'value-3'}
Processing job: job-4 with payload {'data': 'value-4'}
```
LRANGE job_queue 0 -1 → Fetches all elements from start 0 to end -1 of the redis list named job_queue
Redis lists work like a queue with LPUSH/RPUSH and LPOP/RPOP
# once consumer is run- redis gets empty.

further I separated out job queueing from job data

```bash
(.venv) ankitaduttagupta@ANKITAs-MacBook-Air redis-job-queue-system % python3 payload_producer.py 
Enqueued job: job-12aa25f7-9fee-425e-844a-8d5c5df38879
Enqueued job: job-2bae22b8-7d58-4160-8278-6a3d852d0b70
Enqueued job: job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a
Enqueued job: job-1d88f3a2-ed43-4b7f-a6b3-c4c30855bebd
Enqueued job: job-2f28cc48-7c47-494c-8b2e-6d0fe829dd14

127.0.0.1:6379> LRANGE job_queue 0 -1
1) "job-12aa25f7-9fee-425e-844a-8d5c5df38879"
2) "job-2bae22b8-7d58-4160-8278-6a3d852d0b70"
3) "job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a"
4) "job-1d88f3a2-ed43-4b7f-a6b3-c4c30855bebd"
5) "job-2f28cc48-7c47-494c-8b2e-6d0fe829dd14"
127.0.0.1:6379> LRANGE failed_jobs 0 -1
(empty array)
127.0.0.1:6379> hgetall job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a
 1) "file"
 2) "image_2.png"
 3) "action"
 4) "process_image"
 5) "status"
 6) "queued"
 7) "retries"
 8) "0"
 9) "created_at"
10) "1754461389.666352"


(.venv) ankitaduttagupta@ANKITAs-MacBook-Air redis-job-queue-system % python3 payload_consumer.py
Processing: b'job-2bae22b8-7d58-4160-8278-6a3d852d0b70' - {'file': 'image_1.png', 'action': 'process_image', 'status': 'queued', 'retries': '0', 'created_at': '1754461388.656546'}
Success: b'job-2bae22b8-7d58-4160-8278-6a3d852d0b70'
Processing: b'job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a' - {'file': 'image_2.png', 'action': 'process_image', 'status': 'queued', 'retries': '0', 'created_at': '1754461389.666352'}
 Retrying: b'job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a' (attempt 1)
Processing: b'job-1d88f3a2-ed43-4b7f-a6b3-c4c30855bebd' - {'file': 'image_3.png', 'action': 'process_image', 'status': 'queued', 'retries': '0', 'created_at': '1754461390.672222'}
Success: b'job-1d88f3a2-ed43-4b7f-a6b3-c4c30855bebd'
Processing: b'job-2f28cc48-7c47-494c-8b2e-6d0fe829dd14' - {'file': 'image_4.png', 'action': 'process_image', 'status': 'queued', 'retries': '0', 'created_at': '1754461391.678872'}
Success: b'job-2f28cc48-7c47-494c-8b2e-6d0fe829dd14'
Processing: b'job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a' - {'file': 'image_2.png', 'action': 'process_image', 'status': 'retrying', 'retries': '1', 'created_at': '1754461389.666352'}
 Retrying: b'job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a' (attempt 2)
Processing: b'job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a' - {'file': 'image_2.png', 'action': 'process_image', 'status': 'retrying', 'retries': '2', 'created_at': '1754461389.666352'}
 Retrying: b'job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a' (attempt 3)
Processing: b'job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a' - {'file': 'image_2.png', 'action': 'process_image', 'status': 'retrying', 'retries': '3', 'created_at': '1754461389.666352'}
Failed: b'job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a' moved to DLQ
No jobs in queue. Sleeping...
No jobs in queue. Sleeping...
No jobs in queue. Sleeping...



127.0.0.1:6379> keys *
1) "job-2f28cc48-7c47-494c-8b2e-6d0fe829dd14"
2) "job-1d88f3a2-ed43-4b7f-a6b3-c4c30855bebd"
3) "job-12aa25f7-9fee-425e-844a-8d5c5df38879"
4) "failed_jobs"
5) "job-2bae22b8-7d58-4160-8278-6a3d852d0b70"
6) "job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a"

127.0.0.1:6379> lrange failed_jobs 0 -1
1) "job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a"
127.0.0.1:6379> hgetall job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a 
 1) "file"
 2) "image_2.png"
 3) "action"
 4) "process_image"
 5) "status"
 6) "failed"
 7) "retries"
 8) "3"
 9) "created_at"
10) "1754461389.666352"
11) "error"
12) "Simulated failure"
```

Failed jobs can be viewed by executing view_failed_jobs file
```bash
(.venv) ankitaduttagupta@ANKITAs-MacBook-Air redis-job-queue-system % python3 view_failed_jobs.py
Failed Jobs:
Job ID: b'job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a', Data: {b'file': b'image_2.png', b'action': b'process_image', b'status': b'failed', b'retries': b'3', b'created_at': b'1754461389.666352', b'error': b'Simulated failure', 'job_id': b'job-0702cab6-5f7d-4fb2-8d5f-e3fb8698662a'}
```
# Strategy: Graceful Shutdown for a Worker
help the app cleanly start and exit, ensuring Redis connections close, no data is lost,
and workers don’t get stuck halfway.

producer.py → pushes JSON-encoded jobs to list key job_queue.
worker.py → pops from job_queue, processes job, and handles shutdown gracefully.
Jobs will be automatically removed after being processed (with no leftover Redis keys like before).

Start redis - run  worker.py - run  producer.py (in another terminal) - stop  worker cleanly with ctrl+C — to observe

```bash
(.venv) ankitaduttagupta@ANKITAs-MacBook-Air redis-job-queue-system % python3 simple_producer.py
 Worker started. Waiting for jobs...
Processing job: job-0 with payload: {'data': 'value-0'}
 Finished: job-0
Processing job: job-1 with payload: {'data': 'value-1'}
 Finished: job-1
Processing job: job-2 with payload: {'data': 'value-2'}
 Finished: job-2
Processing job: job-3 with payload: {'data': 'value-3'}
 Finished: job-3
Processing job: job-4 with payload: {'data': 'value-4'}
 Finished: job-4
^C
Received signal 2. Preparing to shut down...
^C
Received signal 2. Preparing to shut down...
Exiting worker loop.
Graceful shutdown complete.
```
# Prometheus metrics
<img width="1280" height="832" alt="Screenshot 2025-08-06 at 18 30 15" src="https://github.com/user-attachments/assets/ed49a254-d4d8-4cf2-86bd-11b78c6c956a" />
<img width="1280" height="832" alt="Screenshot 2025-08-06 at 18 29 57" src="https://github.com/user-attachments/assets/4df6518f-5efd-4afc-b216-069b537bee61" />

