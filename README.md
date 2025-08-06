# Redis Job Queue System

This POC demonstrates a lightweight custom job queue using Redis as the backend.

- Enqueue/dequeue jobs using Redis Lists
- Connection pooling via `redis-py`
- Simple retry hooks
- Blocking queue consumption (`BLPOP`)

## How to Run

### 1. Start Redis (locally or via Docker)
```bash
docker run -p 6379:6379 redis
```
to check the redis is working , execute the redis in docker:
```bash
docker exec -it <ur container> redis-cli ping
```

