import redis

_redis_client = None


def get_redis_client():
    global _redis_client
    
    if _redis_client is None:
        _redis_client = redis.Redis(
            host="localhost", 
            port=6379, 
            db=0
        )
        try:
            _redis_client.ping()
        except (redis.ConnectionError, redis.TimeoutError) as e:
            _redis_client = None
            raise ConnectionError("Failed to connect to Redis. Make sure Redis server is running.") from e
        return _redis_client
    else:
        try:
            _redis_client.ping()
        except (redis.ConnectionError, redis.TimeoutError):
            _redis_client = None
            return get_redis_client()
        return _redis_client