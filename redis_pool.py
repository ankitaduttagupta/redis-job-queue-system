import redis

def get_redis_pool():
    return redis.ConnectionPool(host="localhost", port=6379, db=0, max_connections=10)

def get_redis_client():
    pool = get_redis_pool()
    return redis.Redis(connection_pool=pool)

def close_redis_pool():
    pool = get_redis_pool()
    pool.disconnect()
    print("Redis connection pool closed.")
