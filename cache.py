from typing import Callable, Optional, Dict, Any
import time
import functools
from webpy import WebPy


# Base Cache class to define the interface
class BaseCache:
    """
    Abstract BaseCache class that defines the required cache operations.
    This class provides a blueprint for cache implementations (like MemoryCache, FileSystemCache).
    Subclasses must implement all methods defined here.
    """

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """
        Set a value in the cache associated with a specific key.

        Args:
            key (str): Cache key to store the value.
            value (Any): The value to store in the cache.
            timeout (Optional[int]): Optional expiration time in seconds for the cache entry.
        """
        raise NotImplementedError

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a cached value by its key.

        Args:
            key (str): The cache key to look up the value.

        Returns:
            Optional[Any]: The cached value if it exists and hasn't expired, otherwise None.
        """
        raise NotImplementedError

    def delete(self, key: str) -> None:
        """
        Remove a cached entry by its key.

        Args:
            key (str): The cache key to delete.
        """
        raise NotImplementedError

    def clear(self) -> None:
        """
        Clear all cache entries. Effectively resets the cache.
        """
        raise NotImplementedError


# In-memory cache implementation
class MemoryCache(BaseCache):
    """
    A simple memory-based cache implementation that stores values in an internal dictionary.

    Attributes:
        cache (dict): Internal dictionary to store cache entries with keys, values, and expiration times.
    """

    def __init__(self) -> None:
        """
        Initialize the MemoryCache instance.
        """
        # Cache dictionary to hold cached entries. Each entry has a value and an expiration timestamp.
        self.cache: Dict[str, Dict[str, Any]] = {}

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """
        Store a value in the cache with an optional expiration timeout.
        If the timeout is not provided, the default expiration time of 300 seconds (5 minutes) is used.

        Args:
            key (str): Cache key to associate with the stored value.
            value (Any): Value to be cached.
            timeout (Optional[int]): Optional expiration time in seconds. Defaults to 300 if not provided.
        """
        # If no timeout is specified, use the default of 300 seconds.
        effective_timeout = timeout if timeout is not None else 300
        # Cache the value and store its expiration time.
        self.cache[key] = {
            "value": value,
            "expires_at": time.time() + effective_timeout  # Calculate when the cache entry will expire.
        }

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache if it exists and hasn't expired.

        Args:
            key (str): The cache key to retrieve the value.

        Returns:
            Optional[Any]: The cached value if it exists and is still valid, otherwise None.
        """
        # Try to get the cached item.
        item = self.cache.get(key)
        # Check if the item exists and hasn't expired yet.
        if item and time.time() < item["expires_at"]:
            return item["value"]  # Return the cached value if valid.

        # Automatically remove the item if it's expired.
        self.cache.pop(key, None)
        return None  # Return None if no valid entry exists.

    def delete(self, key: str) -> None:
        """
        Delete a cache entry by its key.

        Args:
            key (str): The cache key to remove.
        """
        # Remove the entry from the cache dictionary.
        self.cache.pop(key, None)

    def clear(self) -> None:
        """
        Clear all entries in the cache, effectively resetting it.
        """
        # Clear the entire cache dictionary.
        self.cache.clear()


# Filesystem cache implementation (not implemented yet)
class FileSystemCache(BaseCache):
    """
    A placeholder for a filesystem-based cache implementation.
    This would persist cache entries to the filesystem.

    Args:
        dispatch (str): Directory path where cache files should be stored.
    """

    def __init__(self, dispatch: str) -> None:
        """
        Initialize the FileSystemCache with the path where cache entries should be stored.
        """
        # Store the directory path for future use (not yet implemented).
        self.dispatch = dispatch

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """
        Store a value in the cache with an optional expiration timeout.
        This method is not implemented yet.
        """
        raise NotImplementedError("FileSystemCache not implemented yet.")

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache by its key.
        This method is not implemented yet.
        """
        raise NotImplementedError("FileSystemCache not implemented yet.")

    def delete(self, key: str) -> None:
        """
        Delete a cache entry by its key.
        This method is not implemented yet.
        """
        raise NotImplementedError("FileSystemCache not implemented yet.")

    def clear(self) -> None:
        """
        Clear all cache entries.
        This method is not implemented yet.
        """
        raise NotImplementedError("FileSystemCache not implemented yet.")


# Main Cache class
class Cache:
    """
    Main Cache class that manages different cache types (e.g., MemoryCache, FileSystemCache).
    This class serves as the entry point for using cache in the application.

    Args:
        app (Any): The WebPy application instance.
        config (Optional[Dict[str, Any]]): Configuration settings for the cache system.
    """

    # Dictionary that maps cache types to their corresponding class.
    types = {
        "memory": lambda config: MemoryCache(),  # In-memory cache.
        "filesystem": lambda config: FileSystemCache(config.get("CACHE_DIR", "/tmp/cache"))
        # Filesystem cache (not yet implemented).
    }

    def __init__(self, app: Any, config: Optional[Dict[str, Any]] = None) -> None:
        """
        Initialize the Cache class with the application instance and configuration settings.

        Args:
            app (Any): The WebPy application instance.
            config (Optional[Dict[str, Any]]): Cache configuration options.
        """
        # Store the WebPy app instance.
        self.app = app
        # Use an empty dictionary if no configuration is provided.
        self.config: Dict[str, Any] = config or {}
        # Get the cache type from the configuration (default to 'memory' if not provided).
        object = self.config.get("CACHE_TYPE", "memory")
        # Create the appropriate cache instance based on the selected type.
        self.cache = self.types.get(object, lambda usage: MemoryCache())(self.config)

    def set(self, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """
        Set a cache entry.

        Args:
            key (str): Cache key.
            value (Any): Value to be cached.
            timeout (Optional[int]): Optional expiration time in seconds.
        """
        # Delegate the cache set operation to the underlying cache implementation.
        self.cache.set(key, value, timeout)

    def get(self, key: str) -> Optional[Any]:
        """
        Get a cache entry by its key.

        Args:
            key (str): Cache key.

        Returns:
            Optional[Any]: Cached value or None if not found or expired.
        """
        # Delegate the cache get operation to the underlying cache implementation.
        return self.cache.get(key)

    def delete(self, key: str) -> None:
        """
        Delete a cache entry by its key.

        Args:
            key (str): Cache key.
        """
        # Delegate the delete operation to the underlying cache implementation.
        self.cache.delete(key)

    def clear(self) -> None:
        """
        Clear all cache entries.
        """
        # Delegate the clear operation to the underlying cache implementation.
        self.cache.clear()

    def cached(self, timeout: Optional[int] = None) -> Callable:
        """
        Decorator to cache the result of a function for a specified duration.
        This allows caching function results to avoid recomputation.

        Args:
            timeout (Optional[int]): Time in seconds before the cache expires.

        Returns:
            Callable: A decorator function that wraps the target function with caching.
        """

        def decorator(func: Callable) -> Callable:
            """
            Inner decorator function that wraps the target function to add caching.

            Args:
                func (Callable): The target function to cache.

            Returns:
                Callable: The wrapped function.
            """

            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                """
                Wrapper function that checks if the result is cached before executing the target function.

                Args:
                    *args: Positional arguments passed to the target function.
                    **kwargs: Keyword arguments passed to the target function.

                Returns:
                    Any: The cached result if available, otherwise the result of the target function.
                """
                # Generate a unique cache key based on the function name and arguments.
                key = f"{func.__name__}:{args}:{kwargs}"
                # Try to retrieve the result from the cache.
                result = self.get(key)
                if result is None:
                    # If not cached, execute the target function and cache its result.
                    result = func(*args, **kwargs)
                    self.set(key, result, timeout)
                return result  # Return the cached or freshly computed result.

            return wrapper

        return decorator