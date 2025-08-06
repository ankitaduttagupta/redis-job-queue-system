import redis.asyncio as redis

_redis_pool = None
_redis_client = None

def get_redis_pool():
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.ConnectionPool(host="localhost", port=6379, db=0, max_connections=10, decode_responses=True)
    return _redis_pool

def get_redis_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(connection_pool=get_redis_pool())
    return _redis_client

async def close_redis_pool():
    if _redis_client:
        await _redis_client.close()
        print("Redis client connection closed.")
    if _redis_pool:
        await _redis_pool.disconnect()
        print("Redis connection pool closed.")
