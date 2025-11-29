from abc import ABC, abstractmethod
from typing import Optional

from src.infrastructure.db.models.gitlab import GitLabConfig


class IGitLabRepository(ABC):

    """Class sets the contract by which Application-layer connects with Infrastructure-layer."""

    @abstractmethod
    async def save_config(self, url: str, encrypted_token: str) -> GitLabConfig:
        """Save or update the configuration."""
        raise NotImplementedError

    @abstractmethod
    async def get_config(self) -> Optional[GitLabConfig]:
        """Get current configuration."""
        raise NotImplementedError
