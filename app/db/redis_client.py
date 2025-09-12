import os
from redis import Redis

class RedisClient:
    def __init__(self):
        self.host: str = os.getenv("REDIS_HOST", "localhost")
        self.port: int = int(os.getenv("REDIS_PORT", 6379))
        self.db: int = int(os.getenv("REDIS_DB", 0))
        self._client: Redis = None
        
    def initialize_connection(self) -> None:
        """
        Initialize Redis connection.
        """
        if self._client is None:
            self._client = Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                decode_responses=True
            )
        try:
            self._client.ping()
            print("✅ Connected to Redis")
        except Exception as e:
            print(f"❌ Failed to connect to Redis: {e}")
            raise
    
    def get_client(self) -> Redis:
        """
        Get the Redis client instance.
        
        Returns:
            Redis: The Redis client instance.
        """
        if self._client is None:
            self.initialize_connection()
        return self._client
    
    def check_health(self) -> bool:
        """
        Check if Redis connection is healthy.
        
        Returns:
            bool: True if connection is healthy, False otherwise.
        """
        try:
            return self.get_client().ping()
        except Exception:
            return False
        
    def close(self) -> None:
        """
        Close the Redis connection.
        """
        if self._client:
            self._client.close()
            self._client = None
            print("Redis connection closed")
            
    def get_value(self, key: str) -> str:
        """
        Get a value from Redis by key.
        
        Args:
            key (str): The key to retrieve.
        Returns:
            str: The value associated with the key, or None if not found.
        """
        return self.get_client().get(key)
    
    def set_value(self, key: str, value: str, ttl: int = None) -> None:
        """
        Set a value in Redis with an optional expiration time.
        
        Args:
            key (str): The key to set.
            value (str): The value to associate with the key.
            ttl (int, optional): Expiration time in seconds. Defaults to None.
        """
        self.get_client().set(name=key, value=value, ex=ttl)

    def delete_value(self, key: str) -> int:
        """
        Delete a value from Redis by key.
        Args:
            key (str): The key to delete.
        Returns:
            int: The number of keys that were removed.
        """
        return self.get_client().delete(key)