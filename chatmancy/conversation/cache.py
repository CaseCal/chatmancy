from typing import Protocol, TypeVar, Optional

KT = TypeVar("KT")
VT = TypeVar("VT")


class CacheInterface(Protocol[KT, VT]):
    """
    A protocol for defining the interface of a cache.

    This protocol defines two methods: `get` and `set`. Implementations of this protocol
    should provide concrete implementations of these methods to enable caching of key-value
    pairs.
    """

    def get(self, key: KT) -> Optional[VT]:
        ...

    def set(self, key: KT, value: VT) -> None:
        ...


class DictCache(CacheInterface[KT, VT]):
    """
    A cache implementation that uses a dictionary to store key-value pairs.

    Attributes:
        cache (dict): A dictionary that stores key-value pairs.

    Methods:
        get(key: KT) -> Optional[VT]: Returns the value associated with the given key, or None if the key is not in the cache.
        set(key: KT, value: VT) -> None: Sets the value associated with the given key in the cache.
    """

    def __init__(self):
        self.cache = {}

    def get(self, key: KT) -> Optional[VT]:
        return self.cache.get(key)

    def set(self, key: KT, value: VT) -> None:
        self.cache[key] = value
