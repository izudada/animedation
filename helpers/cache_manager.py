from typing import Any

# from django.conf import settings
from django.core.cache import cache


class CacheManager:
    # TODO: integrate environment in key generation

    @classmethod
    def set_key(cls, key: str, data: Any, timeout: int = None) -> None:
        cache.set(key, data, timeout=timeout)

    @classmethod
    def retrieve_key_ttl(cls, key: str) -> int:
        return cache.ttl(key)

    @classmethod
    def retrieve_key(cls, key: str) -> Any:
        return cache.get(key)

    @classmethod
    def delete_key(cls, key: str) -> None:
        cache.delete(key)

    @classmethod
    def increment_key(cls, key: str)-> None:
        cache.incr(key)
