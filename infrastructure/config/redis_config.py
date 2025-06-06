import redis
from typing import Optional
from infrastructure.config.settings import settings

class RedisConfig:
    """Redis configuration and connection management."""
    
    def __init__(self):
        self._redis_client: Optional[redis.Redis] = None
    
    def get_redis_client(self) -> redis.Redis:
        """Get Redis client instance."""
        if self._redis_client is None:
            self._redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True,  # Important for JSON serialization
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
        return self._redis_client
    
    def test_connection(self) -> bool:
        """Test Redis connection."""
        try:
            client = self.get_redis_client()
            response = client.ping() #type: ignore
            return response is True
        except Exception as e:
            print(f"Redis connection failed: {e}")
            return False

# Global instance
redis_config = RedisConfig()