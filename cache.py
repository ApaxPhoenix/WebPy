import json
import pathlib
from functools import wrap
from typing import Callable, Dict, Any
import appdirs
import time
from webpy import Webpy


class BaseCache:
    """
    Abstract base class defining the core caching interface.
    
    This class serves as a template for different cache implementations,
    enforcing a consistent interface across all cache types. All cache
    implementations must inherit from this class and implement its methods.
    
    Methods:
        set: Store data in the cache with expiration
        get: Retrieve data from the cache
        delete: Remove specific cache entry
        clear: Remove all cache entries
    """

    def set(self, key: str, val: Any, expiry: int = 300) -> None:
        """
        Store a value in the cache with expiration time.

        Args:
            key: Unique identifier for cached item
            val: Data to be cached
            expiry: Seconds until cache entry expires (default: 300)

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError

    def get(self, key: str) -> Any:
        """
        Fetch a value from cache using its key.

        Args:
            key: Unique identifier for cached item

        Returns:
            Any: Cached value if exists and valid, None otherwise

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError

    def delete(self, key: str) -> None:
        """
        Remove specific entry from cache.

        Args:
            key: Unique identifier for cached item

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError

    def clear(self) -> None:
        """
        Remove all entries from cache.

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError


class MemoryCache(BaseCache):
    """
    RAM-based cache implementation using Python dictionary.
    
    This implementation stores all cache data in memory using a dictionary,
    making it fast but volatile. Data is lost when program terminates.
    
    Attributes:
        store: Internal dictionary storing cache entries
    """

    def __init__(self) -> None:
        """Initialize empty cache dictionary."""
        self.store: Dict[str, Dict[str, Any]] = {}

    def set(self, key: str, val: Any, expiry: int = 300) -> None:
        """
        Store value in memory cache with expiration.

        Args:
            key: Unique identifier for cached item
            val: Data to be cached
            expiry: Seconds until cache entry expires (default: 300)
        """
        # Calculate expiration timestamp
        expires = time.time() + expiry
        # Store value and expiration in dictionary
        self.store[key] = {
            "val": val,
            "expires": expires
        }

    def get(self, key: str) -> Any:
        """
        Retrieve value from memory cache.

        Args:
            key: Unique identifier for cached item

        Returns:
            Any: Cached value if valid, None if expired or missing
        """
        entry = self.store.get(key)
        if entry and time.time() < entry["expires"]:
            return entry["val"]
        # Remove expired entry if found
        self.store.pop(key, None)
        return None

    def delete(self, key: str) -> None:
        """
        Remove specific entry from memory cache.

        Args:
            key: Unique identifier for cached item
        """
        self.store.pop(key, None)

    def clear(self) -> None:
        """Remove all entries from memory cache."""
        self.store.clear()


class FileSystemCache(BaseCache):
    """
    File-based cache implementation using JSON files.
    
    This implementation persists cache data to filesystem using JSON format,
    making it persistent but slower than memory cache.
    
    Attributes:
        cachedir: Path to directory storing cache files
    """

    def __init__(self, directory: str = None) -> None:
        """
        Initialize filesystem cache.

        Args:
            directory: Custom cache directory path (default: system cache dir)
        """
        self.cachedir = pathlib.Path(directory or appdirs.user_cache_dir())
        # Ensure cache directory exists
        self.cachedir.mkdir(parents=True, exist_ok=True)

    def set(self, key: str, val: Any, expiry: int = 300) -> None:
        """
        Store value in filesystem cache.

        Args:
            key: Unique identifier for cached item
            val: Data to be cached
            expiry: Seconds until cache entry expires (default: 300)
        """
        filepath = pathlib.Path(self.cachedir, f"{key}.json")
        expires = time.time() + expiry
        data = {"val": val, "expires": expires}
        # Write cache entry to JSON file
        with open(filepath, "w") as file:
            json.dump(data, file)

    def get(self, key: str) -> Any:
        """
        Retrieve value from filesystem cache.

        Args:
            key: Unique identifier for cached item

        Returns:
            Any: Cached value if valid, None if expired or missing
        """
        filepath = pathlib.Path(self.cachedir, f"{key}.json")
        if filepath.exists():
            with open(filepath, "r") as file:
                data = json.load(file)
            if time.time() < data["expires"]:
                return data["val"]
            # Remove expired cache file
            filepath.unlink()
        return None

    def delete(self, key: str) -> None:
        """
        Remove specific entry from filesystem cache.

        Args:
            key: Unique identifier for cached item
        """
        filepath = pathlib.Path(self.cachedir, f"{key}.json")
        if filepath.exists():
            filepath.unlink()

    def clear(self) -> None:
        """Remove all JSON files from cache directory."""
        for file in self.cachedir.glob("*.json"):
            file.unlink()


class Cache:
    """
    Unified cache interface supporting multiple backend types.
    
    This class provides a high-level interface for caching operations,
    supporting both memory and filesystem backends with consistent API.
    
    Attributes:
        types: Dictionary mapping cache type names to their implementations
        app: Application context (optional)
        config: Cache configuration dictionary
        backend: Active cache backend instance
    """

    # Available cache backend types
    types = {
        "memory": lambda cfg: MemoryCache(),
        "filesystem": lambda cfg: FileSystemCache(cfg.get("CACHE_DIR"))
    }

    def __init__(self, app: WebPy, config: Dict[str, Any] = None) -> None:
        """
        Initialize cache system.

        Args:
            app: Application context (optional)
            config: Configuration dictionary with CACHE_TYPE and CACHE_DIR
        """
        self.app = app
        self.config = config or {}
        # Get cache type from config or default to memory
        cachetype = self.config.get("CACHE_TYPE", "memory")
        # Initialize appropriate cache backend
        self.backend = self.types.get(cachetype, lambda _: MemoryCache())(self.config)

    def set(self, key: str, val: Any, expiry: int = 300) -> None:
        """
        Store value in active cache backend.

        Args:
            key: Unique identifier for cached item
            val: Data to be cached
            expiry: Seconds until cache entry expires (default: 300)
        """
        self.backend.set(key, val, expiry)

    def get(self, key: str) -> Any:
        """
        Retrieve value from active cache backend.

        Args:
            key: Unique identifier for cached item

        Returns:
            Any: Cached value if valid, None if expired or missing
        """
        return self.backend.get(key)

    def delete(self, key: str) -> None:
        """
        Remove specific entry from active cache backend.

        Args:
            key: Unique identifier for cached item
        """
        self.backend.delete(key)

    def clear(self) -> None:
        """Remove all entries from active cache backend."""
        self.backend.clear()

    def cached(self, expiry: int = 300) -> Callable:
        """
        Decorator for caching function results.

        Creates a wrapper that caches function return values,
        using function name and arguments as cache key.

        Args:
            expiry: Seconds until cached results expire (default: 300)

        Returns:
            Callable: Decorated function with caching
        """

        def decorator(func: Callable) -> Callable:
            """
            Inner decorator applying caching to function.

            Args:
                func: Function to be cached

            Returns:
                Callable: Wrapped function with caching
            """

            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                """
                Wrapper handling cache lookup and storage.

                Args:
                    *args: Positional arguments to cached function
                    **kwargs: Keyword arguments to cached function

                Returns:
                    Any: Cached or fresh function result
                """
                # Generate unique cache key from function name and arguments
                cachekey = f"{func.__name__}:{args}:{kwargs}"
                # Try to get cached result
                result = self.get(cachekey)
                if result is None:
                    # Cache miss - execute function and store result
                    result = func(*args, **kwargs)
                    self.set(cachekey, result, expiry)
                return result

            return wrapper

        return decorator
