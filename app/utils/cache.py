import json
import time
import logging
from app.db.redis_client import RedisClient

logger = logging.getLogger("cache")

class Cache:
    def __init__(self, redis_client: RedisClient):
        self.client = redis_client
        self.is_connected = False
        self.hits = 0
        self.misses = 0
        self.total_db_time_saved = 0
        
        try:
            self.client.initialize_connection()
            self.is_connected = True
            logger.info("Cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            logger.warning("Cache will operate in fallback mode (no caching)")
    
    def serialize_object(self, obj) -> str:
        """
        Serialize an object to a string for caching.
        
        Args:
            obj: The object to serialize.
        Returns:
            str: The serialized object.
        """
        return json.dumps(obj, default=str)

    def deserialize_object(self, data: str):
        """
        Deserialize a string back into an object.
        Args:
            data (str): The serialized string to deserialize.
        Returns:
            The deserialized object.
        """
        return json.loads(data)
    
    def generate_key(self, *args) -> str:
        """
        Generate a cache key based on provided arguments.
        
        Args:
            *args: Components to include in the key.
        Returns:
            str: The generated cache key.
        """
        return ":".join(map(str, args))
    
    def get_cached(self, key: str):
        """
        Retrieve an object from the cache.
        
        Args:
            key (str): The cache key.
        Returns:
            The cached object or None if not found.
        """
        if not self.is_connected:
            self.misses += 1
            return None
            
        try:
            start_time = time.time()
            data = self.client.get_value(key)
            if data:
                self.hits += 1
                result = self.deserialize_object(data)
                logger.debug(f"Cache HIT: {key}")
                return result
            else:
                self.misses += 1
                logger.debug(f"Cache MISS: {key}")
        except Exception as e:
            self.misses += 1
            logger.error(f"Cache get error: {e}")
        return None
    
    def set_cache(self, key: str, obj, ttl: int = 3600) -> None:
        """
        Store an object in the cache.
        
        Args:
            key (str): The cache key.
            obj: The object to cache.
            ttl (int): Time to live in seconds. Default is 3600 seconds (1 hour).
        """
        if not self.is_connected:
            return
            
        try:
            serialized_obj = self.serialize_object(obj)
            self.client.set_value(key, serialized_obj, ttl)
        except Exception as e:
            print(f"Cache set error: {e}")
    
    def delete_cache(self, key: str) -> int:
        """
        Delete an object from the cache.
        
        Args:
            key (str): The cache key.
        Returns:
            int: Number of keys that were removed.
        """
        if not self.is_connected:
            return 0
            
        try:
            return self.client.delete_value(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
            return 0
    
    def clear_cache(self) -> None:
        """
        Clear the entire cache.
        """
        if not self.is_connected:
            return
            
        try:
            self.client.get_client().flushdb()
        except Exception as e:
            print(f"Cache clear error: {e}")
        
    def invalidate(self, pattern: str) -> None:
        """
        Invalidate cache entries matching a pattern.
        
        Args:
            pattern (str): The pattern to match keys against.
        """
        if not self.is_connected:
            return
            
        try:
            keys = self.client.get_client().keys(pattern)
            if keys:
                self.client.get_client().delete(*keys)
        except Exception as e:
            print(f"Cache invalidate error: {e}")