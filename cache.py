import json
import pathlib
import functools
from typing import Callable, Dict, Any
import appdirs
import time


# Base Cache class to define the interface
class BaseCache:
    """
    Abstract BaseCache class defining the required cache operations.
    Subclasses must implement all methods to ensure functionality.
    """

    def set(self, cache_key: str, cache_value: Any, cache_timeout: int = 300) -> None:
        """
        Store a value in the cache with an expiration time.

        Args:
            cache_key: Unique identifier for the cache item.
            cache_value: Data to store in the cache.
            cache_timeout: Time in seconds until the cache expires (default is 300).
        """
        raise NotImplementedError

    def get(self, cache_key: str) -> Any:
        """
        Retrieve a value from the cache by its key.

        Args:
            cache_key: Unique identifier for the cache item.

        Returns:
            The cached value if it exists and hasn't expired, otherwise None.
        """
        raise NotImplementedError

    def delete(self, cache_key: str) -> None:
        """
        Remove a specific cache entry by its key.

        Args:
            cache_key: Unique identifier for the cache item.
        """
        raise NotImplementedError

    def clear(self) -> None:
        """
        Remove all items from the cache.
        """
        raise NotImplementedError


# In-memory cache implementation
class MemoryCache(BaseCache):
    """
    Simple in-memory cache that stores data in a Python dictionary.
    """

    def __init__(self) -> None:
        """
        Initialize an internal dictionary for cache storage.
        """
        self.memory_cache: Dict[str, Dict[str, Any]] = {}

    def set(self, cache_key: str, cache_value: Any, cache_timeout: int = 300) -> None:
        """
        Store a value in the memory cache with an expiration time.
        """
        self.memory_cache[cache_key] = {
            "value": cache_value,
            "expires": time.time() + cache_timeout  # Expiration timestamp
        }

    def get(self, cache_key: str) -> Any:
        """
        Retrieve a value from the memory cache if it exists and hasn't expired.
        """
        cache_item = self.memory_cache.get(cache_key)
        if cache_item and time.time() < cache_item["expires"]:
            return cache_item["value"]
        self.memory_cache.pop(cache_key, None)  # Remove expired or missing entry
        return None

    def delete(self, cache_key: str) -> None:
        """
        Delete a specific cache entry by its key.
        """
        self.memory_cache.pop(cache_key, None)

    def clear(self) -> None:
        """
        Clear all entries in the memory cache.
        """
        self.memory_cache.clear()


# Filesystem cache implementation
class FileSystemCache(BaseCache):
    """
    Filesystem-based cache storing data as JSON files in a specified directory.
    """

    def __init__(self, cache_directory: str = None) -> None:
        """
        Initialize the filesystem cache.

        Args:
            cache_directory: Path to the cache directory (defaults to appdirs' user cache directory).
        """
        self.cache_directory = pathlib.Path(cache_directory or appdirs.user_cache_dir())
        self.cache_directory.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

    def set(self, cache_key: str, cache_value: Any, cache_timeout: int = 300) -> None:
        """
        Store a value in the filesystem cache with an expiration time.
        """
        file_path = pathlib.Path(self.cache_directory, f"{cache_key}.json")
        expires = time.time() + cache_timeout
        cache_entry = {"value": cache_value, "expires": expires}
        with open(file_path, "w") as file:
            json.dump(cache_entry, file)

    def get(self, cache_key: str) -> Any:
        """
        Retrieve a value from the filesystem cache if it exists and hasn't expired.
        """
        file_path = pathlib.Path(self.cache_directory, f"{cache_key}.json")
        if file_path.exists():
            with open(file_path, "r") as file:
                cache_entry = json.load(file)
            if time.time() < cache_entry["expires"]:
                return cache_entry["value"]
            file_path.unlink()  # Delete expired cache file
        return None

    def delete(self, cache_key: str) -> None:
        """
        Delete a specific cache file by its key.
        """
        file_path = pathlib.Path(self.cache_directory, f"{cache_key}.json")
        if file_path.exists():
            file_path.unlink()

    def clear(self) -> None:
        """
        Remove all cache files in the cache directory.
        """
        for file in self.cache_directory.glob("*.json"):
            file.unlink()


# Main Cache class
class Cache:
    """
    Unified interface to manage caching, supporting memory and filesystem caching.
    """

    cache_types = {
        "memory": lambda config: MemoryCache(),
        "filesystem": lambda config: FileSystemCache(config.get("CACHE_DIR", appdirs.user_cache_dir()))
    }

    def __init__(self, app_context: Any, config_dict: Dict[str, Any] = None) -> None:
        """
        Initialize the Cache object.

        Args:
            app_context: Application context (optional).
            config_dict: Configuration dictionary (e.g., CACHE_TYPE and CACHE_DIR).
        """
        self.app_context = app_context
        self.config_dict = config_dict or {}
        cache_type = self.config_dict.get("CACHE_TYPE", "memory")
        self.cache = self.cache_types.get(cache_type, lambda _: MemoryCache())(self.config_dict)

    def set(self, cache_key: str, cache_value: Any, cache_timeout: int = 300) -> None:
        """
        Store a value in the cache with an expiration time.
        """
        self.cache.set(cache_key, cache_value, cache_timeout)

    def get(self, cache_key: str) -> Any:
        """
        Retrieve a value from the cache.
        """
        return self.cache.get(cache_key)

    def delete(self, cache_key: str) -> None:
        """
        Delete a specific cache entry by its key.
        """
        self.cache.delete(cache_key)

    def clear(self) -> None:
        """
        Clear all cached items.
        """
        self.cache.clear()

    def cached(self, cache_timeout: int = 300) -> Callable:
        """
        Decorator to cache the result of a function for a specified duration.
        """

        def decorator(func: Callable) -> Callable:

            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                cache_key = f"{func.__name__}:{args}:{kwargs}"
                cached_result = self.get(cache_key)
                if cached_result is None:
                    cached_result = func(*args, **kwargs)
                    self.set(cache_key, cached_result, cache_timeout)
                return cached_result

            return wrapper

        return decorator
