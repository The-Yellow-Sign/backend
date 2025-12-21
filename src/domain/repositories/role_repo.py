from abc import ABC, abstractmethod
from typing import List, Optional

from src.domain.models.user import Role as DomainRole


class IRoleRepository(ABC):

    """Class sets the contract by which Application-layer connects with Infrastructure-layer."""

    @abstractmethod
    async def create(self, role: DomainRole) -> Optional[DomainRole]:
        """Create new role and put it in db."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_name(self, role_name: str) -> Optional[DomainRole]:
        """Get info about role by its name."""
        raise NotImplementedError

    @abstractmethod
    async def get_all_roles(self) -> List[DomainRole]:
        """Get list of all existing roles."""
        raise NotImplementedError
