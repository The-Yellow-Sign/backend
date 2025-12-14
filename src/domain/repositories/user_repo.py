from abc import ABC, abstractmethod
from typing import List, Optional

from pydantic import UUID4, EmailStr

from src.domain.models.user import User as DomainUser


class IUserRepository(ABC):

    """Class sets the contract by which Application-layer connects with Infrastructure-layer."""

    @abstractmethod
    async def get_all_users(self) -> List[DomainUser]:
        """Retrieve all existing users from db."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_username(self, username: str) -> Optional[DomainUser]:
        """Retrieve user from db by username."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_email(self, email: EmailStr) -> Optional[DomainUser]:
        """Retrieve user from db by email adress."""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: UUID4) -> Optional[DomainUser]:
        """Retrieve user from db by id."""
        raise NotImplementedError

    @abstractmethod
    async def create(self, user: DomainUser) -> DomainUser:
        """Create new user and put them in db."""
        raise NotImplementedError

    @abstractmethod
    async def update(self, user: DomainUser) -> Optional[DomainUser]:
        """Update info about existing user."""
        raise NotImplementedError
