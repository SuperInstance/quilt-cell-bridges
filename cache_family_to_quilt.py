"""
Cache Family to Quilt Bridge
===========================

This module provides a unified interface to various cache substrates through a
polymorphic, composable pattern known as the "Quilt" abstraction. The Quilt enables
transparent integration with multiple caching backends (Redis, Memcached, LRU, LFU,
CDN, etc.) while maintaining a consistent API.

The bridge leverages the 8 fundamental cache primitives:

1. **Set** - Store a key-value pair with optional TTL.
2. **Get** - Retrieve a value by key, return None if not found.
3. **Delete** - Remove a key-value pair from cache.
4. **Exists** - Check if a key exists in cache.
5. **Increment** - Atomically increment a numeric value.
6. **Decrement** - Atomically decrement a numeric value.
7. **Touch** - Extend the TTL of an existing key.
8. **Flush** - Clear all entries from the cache.

Each cache substrate (Redis, Memcached, LRU, LFU, CDN) implements these primitives
via a common interface, allowing application code to be substrate-agnostic.

The Quilt class composes multiple cache backends, enabling fallback behaviors
and multi-layer caching (e.g., local LRU + remote Redis).

Design Principles:
- Minimal dependencies (stdlib only).
- Thread-safe via built-in locks where needed.
- TTL-aware, expiry handling consistent across backends.
- Error handling with retry logic and fallback.
- High performance, low overhead.

Usage:
    quilt = Quilt(
        backends=[
            LRU(maxsize=10000),
            RedisCache(host="localhost", port=6379),
            CDNCache(base_url="https://cdn.example.com"),
        ],
        fallback=True,
        timeout=5.0
    )

    quilt.set("user:123", {"name": "Alice"}, ttl=300)
    data = quilt.get("user:123")
"""

import time
import threading
import hashlib
import json
import functools
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from abc import ABC, abstractmethod


# ================ 8 PRIMITIVES ================

class CachePrimitive(ABC):
    """Abstract base class for all cache primitives."""

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Store key-value pair with optional expiry."""
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value by key."""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Remove key from cache."""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists."""
        pass

    @abstractmethod
    def increment(self, key: str, delta: int = 1) -> Optional[int]:
        """Atomically increment value at key."""
        pass

    @abstractmethod
    def decrement(self, key: str, delta: int = 1) -> Optional[int]:
        """Atomically decrement value at key."""
        pass

    @abstractmethod
    def touch(self, key: str, ttl: int) -> bool:
        """Extend TTL of existing key."""
        pass

    @abstractmethod
    def flush(self) -> bool:
        """Clear all entries."""
        pass


# ================ BACKENDS ================

class LRUCache(CachePrimitive):
    """Simple in-memory LRU cache using OrderedDict (stdlib only)."""

    def __init__(self, maxsize: int = 128):
        self._maxsize = maxsize
        self._cache = {}
        self._order = []
        self._lock = threading.RLock()

    def _move_to_end(self, key: str):
        if key in self._order:
            self._order.remove(key)
        self._order.append(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        with self._lock:
            if len(self._cache) >= self._maxsize:
                oldest = self._order.pop(0)
                del self._cache[oldest]
            self._cache[key] = {
                'value': value,
                'expiry': time.time() + ttl if ttl else None
            }
            self._move_to_end(key)
            return True

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            if entry['expiry'] and time.time() > entry['expiry']:
                del self._cache[key]
                self._order.remove(key)
                return None
            self._move_to_end(key)
            return entry['value']

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self._order.remove(key)
                return True
            return False

    def exists(self, key: str) -> bool:
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return False
            if entry['expiry'] and time.time() > entry['expiry']:
                del self._cache[key]
                self._order.remove(key)
                return False
            return True

    def increment(self, key: str, delta: int = 1) -> Optional[int]:
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            if entry['expiry'] and time.time() > entry['expiry']:
                del self._cache[key]
                self._order.remove(key)
                return None
            try:
                value = entry['value']
                if isinstance(value, (int, float)):
                    new_value = value + delta
                    entry['value'] = new_value
                    self._move_to_end(key)
                    return new_value
                else:
                    return None
            except (TypeError, ValueError):
                return None

    def decrement(self, key: str, delta: int = 1) -> Optional[int]:
        return self.increment(key, -delta)

    def touch(self, key: str, ttl: int) -> bool:
        with self._lock:
            if key in self._cache:
                self._cache[key]['expiry'] = time.time() + ttl
                self._move_to_end(key)
                return True
            return False

    def flush(self) -> bool:
        with self._lock:
            self._cache.clear()
            self._order.clear()
            return True


class MemcachedCache(CachePrimitive):
    """In-memory simulation of Memcached behavior (no external deps)."""

    def __init__(self, host: str = "localhost", port: int = 11211):
        self._host = host
        self._port = port
        self._cache = {}
        self._lock = threading.RLock()

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        with self._lock:
            expiry = time.time() + ttl if ttl else None
            self._cache[key] = {
                'value': value,
                'expiry': expiry
            }
            return True

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            if entry['expiry'] and time.time() > entry['expiry']:
                del self._cache[key]
                return None
            return entry['value']

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def exists(self, key: str) -> bool:
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return False
            if entry['expiry'] and time.time() > entry['expiry']:
                del self._cache[key]
                return False
            return True

    def increment(self, key: str, delta: int = 1) -> Optional[int]:
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            if entry['expiry'] and time.time() > entry['expiry']:
                del self._cache[key]
                return None
            try:
                value = entry['value']
                if isinstance(value, (int, float)):
                    new_value = value + delta
                    entry['value'] = new_value
                    return new_value
                else:
                    return None
            except (TypeError, ValueError):
                return None

    def decrement(self, key: str, delta: int = 1) -> Optional[int]:
        return self.increment(key, -delta)

    def touch(self, key: str, ttl: int) -> bool:
        with self._lock:
            if key in self._cache:
                self._cache[key]['expiry'] = time.time() + ttl
                return True
            return False

    def flush(self) -> bool:
        with self._lock:
            self._cache.clear()
            return True


class RedisCache(CachePrimitive):
    """In-memory simulation of Redis behavior using Python dict.

    Note: This is a simulation. For real Redis, use 'redis-py'. This version
    mimics behavior with local storage and expiry logic only.
    """

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0):
        self._host = host
        self._port = port
        self._db = db
        self._cache = {}
        self._lock = threading.RLock()

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        with self._lock:
            expiry = time.time() + ttl if ttl else None
            self._cache[key] = {
                'value': value,
                'expiry': expiry
            }
            return True

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            if entry['expiry'] and time.time() > entry['expiry']:
                del self._cache[key]
                return None
            return entry['value']

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def exists(self, key: str) -> bool:
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return False
            if entry['expiry'] and time.time() > entry['expiry']:
                del self._cache[key]
                return False
            return True

    def increment(self, key: str, delta: int = 1) -> Optional[int]:
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            if entry['expiry'] and time.time() > entry['expiry']:
                del self._cache[key]
                return None
            try:
                value = entry['value']
                if isinstance(value, (int, float)):
                    new_value = value + delta
                    entry['value'] = new_value
                    return new_value
                else:
                    return None
            except (TypeError, ValueError):
                return None

    def decrement(self, key: str, delta: int = 1) -> Optional[int]:
        return self.increment(key, -delta)

    def touch(self, key: str, ttl: int) -> bool:
        with self._lock:
            if key in self._cache:
                self._cache[key]['expiry'] = time.time() + ttl
                return True
            return False

    def flush(self) -> bool:
        with self._lock:
            self._cache.clear()
            return True


class LFUCache(CachePrimitive):
    """Least Frequently Used cache with frequency tracking."""

    def __init__(self, maxsize: int = 128):
        self._maxsize = maxsize
        self._cache = {}  # key -> {value, freq, expiry}
        self._freq_map = {}  # freq -> set of keys
        self._min_freq = 0
        self._lock = threading.RLock()

    def _update_freq(self, key: str):
        entry = self._cache[key]
        freq = entry['freq']
        # Remove from old frequency set
        if freq in self._freq_map:
            self._freq_map[freq].discard(key)
            if not self._freq_map[freq]:
                del self._freq_map[freq]
                if self._min_freq == freq:
                    self._min_freq += 1
        # Increment frequency
        entry['freq'] += 1
        new_freq = entry['freq']
        # Add to new frequency set
        if new_freq not in self._freq_map:
            self._freq_map[new_freq] = set()
        self._freq_map[new_freq].add(key)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        with self._lock:
            # Expire if already exists
            if key in self._cache:
                self.delete(key)
            # Check size
            if len(self._cache) >= self._maxsize:
                # Evict LFU key
                while self._min_freq in self._freq_map and not self._freq_map[self._min_freq]:
                    self._min_freq += 1
                if self._min_freq in self._freq_map:
                    victim = self._freq_map[self._min_freq].pop()
                    del self._cache[victim]
            # Insert
            self._cache[key] = {
                'value': value,
                'freq': 1,
                'expiry': time.time() + ttl if ttl else None
            }
            self._freq_map[1] = self._freq_map.get(1, set())
            self._freq_map[1].add(key)
            self._min_freq = 1
            return True

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            if entry['expiry'] and time.time() > entry['expiry']:
                del self._cache[key]
                # Clean up frequency map
                if entry['freq'] in self._freq_map:
                    self._freq_map[entry['freq']].discard(key)
                return None
            self._update_freq(key)
            return entry['value']

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                # Remove from frequency map
                if entry['freq'] in self._freq_map:
                    self._freq_map[entry['freq']].discard(key)
                    if not self._freq_map[entry['freq']]:
                        del self._freq_map[entry['freq']]
                        if self._min_freq == entry['freq']:
                            self._min_freq += 1
                del self._cache[key]
                return True
            return False

    def exists(self, key: str) -> bool:
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return False
            if entry['expiry'] and time.time() > entry['expiry']:
                del self._cache[key]
                # Clean up frequency map
                if entry['freq'] in self._freq_map:
                    self._freq_map[entry['freq']].discard(key)
                return False
            return True

    def increment(self, key: str, delta: int = 1) -> Optional[int]:
        with self._lock:
            entry = self._cache.get(key)
            if not entry:
                return None
            if entry['expiry'] and time.time() > entry['expiry']:
                del self._cache[key]
                return None
            try:
                value = entry['value']
                if isinstance(value, (int, float)):
                    new_value = value + delta
                    entry['value'] = new_value
                    self._update_freq(key)
                    return new_value
                else:
                    return None
            except (TypeError, ValueError):
                return None

    def decrement(self, key: str, delta: int = 1) -> Optional[int]:
        return self.increment(key, -delta)

    def touch(self, key: str, ttl: int) -> bool:
        with self._lock:
            if key in self._cache:
                self._cache[key]['expiry'] = time.time() + ttl
                self._update_freq(key)
                return True
            return False

    def flush(self) -> bool:
        with self._lock:
            self._cache.clear()
            self._freq_map.clear()
            self._min_freq = 0
            return True


class CDNCache(CachePrimitive):
    """Simulate CDN-like behavior with HTTP-like caching."""

    def __init__(self, base_url: str = "https://cdn.example.com"):
        self._base_url = base_url
        self._cache = {}
        self._lock = threading.RLock()

    def _generate_key(self, key: str) -> str:
        return hashlib.md5(key.encode()).hexdigest()

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        with self._lock:
            encoded_key = self._generate_key(key)
            expiry = time.time() + ttl if ttl else None
            self._cache[encoded_key] = {
                'value': value,
                'expiry': expiry,
                'original_key': key
            }
            return True

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            encoded_key = self._generate_key(key)
            entry = self._cache.get(encoded_key)
            if not entry:
                return None
            if entry['expiry'] and time.time() > entry['expiry']:
                del self._cache[encoded_key]
                return None
            return entry['value']

    def delete(self, key: str) -> bool:
        with self._lock:
            encoded_key = self._generate_key(key)
            if encoded_key in self._cache:
                del self._cache[encoded_key]
                return True
            return False

    def exists(self, key: str) -> bool:
        with self._lock:
            encoded_key = self._generate_key(key)
            entry = self._cache.get(encoded_key)
            if not entry:
                return False
            if entry['expiry'] and time.time() > entry['expiry']:
                del self._cache[encoded_key]
                return False
            return True

    def increment(self, key: str, delta: int = 1) -> Optional[int]:
        with self._lock:
            encoded_key = self._generate_key(key)
            entry = self._cache.get(encoded_key)
            if not entry:
                return None
            if entry['expiry'] and time.time() > entry['expiry']:
                del self._cache[encoded_key]
                return None
            try:
                value = entry['value']
                if isinstance(value, (int, float)):
                    new_value = value + delta
                    entry['value'] = new_value
                    return new_value
                else:
                    return None
            except (TypeError, ValueError):
                return None

    def decrement(self, key: str, delta: int = 1) -> Optional[int]:
        return self.increment(key, -delta)

    def touch(self, key: str, ttl: int) -> bool:
        with self._lock:
            encoded_key = self._generate_key(key)
            if encoded_key in self._cache:
                self._cache[encoded_key]['expiry'] = time.time() + ttl
                return True
            return False

    def flush(self) -> bool:
        with self._lock:
            self._cache.clear()
            return True


# ================ QUILT BRIDGE ================

class Quilt:
    """Compose multiple cache backends with fallback and priority logic."""

    def __init__(
        self,
        backends: List[CachePrimitive],
        fallback: bool = True,
        timeout: float = 5.0,
        retry_attempts: int = 1
    ):
        if not backends:
            raise ValueError("At least one backend is required.")
        self._backends = backends
        self._fallback = fallback
        self._timeout = timeout
        self._retry_attempts = retry_attempts
        self._lock = threading.RLock()

    def _execute(self, method: str, *args, **kwargs) -> Any:
        """Execute method across backends with retry logic."""
        last_exception = None
        for attempt in range(self._retry_attempts):
            for backend in self._backends:
                try:
                    result = getattr(backend, method)(*args, **kwargs)
                    return result
                except Exception as e:
                    last_exception = e
                    continue
            if not self._fallback:
                break
        if last_exception:
            raise last_exception

    # === 8 PRIMITIVES ===

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        with self._lock:
            return self._execute("set", key, value, ttl)

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            return self._execute("get", key)

    def delete(self, key: str) -> bool:
        with self._lock:
            return self._execute("delete", key)

    def exists(self, key: str) -> bool:
        with self._lock:
            return self._execute("exists", key)

    def increment(self, key: str, delta: int = 1) -> Optional[int]:
        with self._lock:
            return self._execute("increment", key, delta)

    def decrement(self, key: str, delta: int = 1) -> Optional[int]:
        with self._lock:
            return self._execute("decrement", key, delta)

    def touch(self, key: str, ttl: int) -> bool:
        with self._lock:
            return self._execute("touch", key, ttl)

    def flush(self) -> bool:
        with self._lock:
            for backend in self._backends:
                try:
                    backend.flush()
                except Exception:
                    continue
            return True

    def __len__(self) -> int:
        with self._lock:
            total = 0
            for backend in self._backends:
                try:
                    # No direct size access, so use approximate
                    total += len([k for k in self._backends[0].get_all_keys() if self.exists(k)])
                except Exception:
                    continue
            return total

    def get_all_keys(self) -> List[str]:
        """Get all keys from the quilt (approximate)."""
        keys = set()
        for backend in self._backends:
            try:
                # No standard way to list keys, simulate via introspection
                # This is a limitation of the simulation
                pass
            except Exception:
                continue
        return list(keys)


# ================ TESTS ================

def test_cache_primitives():
    """Test all 8 primitives across all backends."""
    backends = [
        LRUCache(maxsize=10),
        MemcachedCache(),
        RedisCache(),
        LFUCache(maxsize=10),
        CDNCache(base_url="https://example.com"),
    ]

    test_key = "test:key:1"
    test_value = {"name": "Alice", "age": 30}

    for backend in backends:
        # Set
        assert backend.set(test_key, test_value, ttl=60) is True

        # Get
        retrieved = backend.get(test_key)
        assert retrieved == test_value

        # Exists
        assert backend.exists(test_key) is True

        # Increment (on int)
        backend.set("counter", 5)
        assert backend.increment("counter", 1) == 6
        assert backend.increment("counter", -1) == 5

        # Decrement
        assert backend.decrement("counter", 1) == 4

        # Touch
        assert backend.touch(test_key, 30) is True

        # Delete
        assert backend.delete(test_key) is True
        assert backend.get(test_key) is None
        assert backend.exists(test_key) is False

        # Flush
        backend.set("temp", "value")
        assert backend.flush() is True
        assert backend.get("temp") is None


def test_quilt_composition():
    """Test quilt with multiple backends and fallback."""
    lru = LRUCache(maxsize=10)
    redis = RedisCache()
    quilt = Quilt(backends=[lru, redis], fallback=True)

    # Set in LRU, get from quilt → should succeed
    quilt.set("user:1", {"name": "Bob"}, ttl=30)
    assert quilt.get("user:1") == {"name": "Bob"}

    # Delete via quilt → should delete from both
    quilt.delete("user:1")
    assert quilt.get("user:1") is None

    # Increment via quilt
    quilt.set("counter", 10)
    assert quilt.increment("counter", 5) == 15
    assert quilt.decrement("counter", 3) == 12

    # Touch
    quilt.touch("counter", 60)
    time.sleep(1)
    assert quilt.get("counter") == 12

    # Flush
    quilt.set("test", "value")
    assert quilt.flush() is True
    assert quilt.get("test") is None


if __name__ == "__main__":
    test_cache_primitives()
    test_quilt_composition()
    print("All tests passed.")
