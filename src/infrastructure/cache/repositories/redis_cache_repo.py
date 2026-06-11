import json
from typing import List, Optional
from uuid import UUID

from redis.asyncio import Redis

from src.core.settings import settings
from src.domain.models.chat import Message
from src.domain.repositories.cache_repo import ICacheRepository


class RedisCacheRepository(ICacheRepository):

    """Cache's repository realisation for Redis."""

    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    def construct_cache_key(self, query: str, repository_ids: List[UUID]) -> str:
        """Construct cache key."""
        repository_ids = [str(repository_id) for repository_id in repository_ids]
        sorted_ids = sorted(repository_ids)

        return f"{';'.join(sorted_ids)}:{query}"

    async def get_cached_value(self, key: str) -> Optional[Message]:
        """Get value from cache by given key. Return None if key isn't in cache yet."""
        value = await self.redis.get(key)

        if not value:
            return None

        try:
            return Message.model_validate_json(value)
        except json.JSONDecodeError as error:
            raise ValueError("Invalid JSON format from cache.") from error

    async def put_cache_value(self, key: str, message: Message) -> None:
        """Put value to key with given key."""
        json_data = message.model_dump_json()

        await self.redis.set(
            name=key,
            value=json_data,
            ex=settings.CACHE_TTL
        )
