from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.models.chat import Message


class ICacheRepository(ABC):

    """Class sets the contract by which Application-layer connects with Infrastructure-layer."""

    @abstractmethod
    def construct_cache_key(self, query: str, repository_ids: List[UUID]) -> str:
        """Construct cache key."""
        raise NotImplementedError

    @abstractmethod
    async def get_cached_value(self, key: str) -> Optional[Message]:
        """Get value from cache by given key. Return None if key isn't in cache yet."""
        raise NotImplementedError

    @abstractmethod
    async def put_cache_value(self, key: str, message: Message) -> None:
        """Put value to key with given key."""
        raise NotImplementedError
