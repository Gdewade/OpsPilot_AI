import redis

# Connect to the Redis server
redis_client = redis.Redis(
    host="localhost",
    port=6379,
    decode_responses=True
)

# Check Redis connection
def check_redis_connection():
    try:
        return redis_client.ping()
    except redis.RedisError:
        return False