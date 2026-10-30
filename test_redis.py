from app.core.redis_client import check_redis_connection

if check_redis_connection():
    print("Redis connection successful!")
else:
    print("Redis connection failed!")