import uuid
from typing import List

from fastapi import HTTPException, status
from pydantic import UUID4

from src.api.schemas.admin import RoleCreate
from src.domain.models.user import Role as DomainRole, User as DomainUser
from src.domain.repositories.role_repo import IRoleRepository
from src.domain.repositories.user_repo import IUserRepository


class AdminService:

    """Provides methods for managing users, roles, and permissions."""

    def __init__(self, user_repo: IUserRepository, role_repo: IRoleRepository):
        self.user_repo = user_repo
        self.role_repo = role_repo

    async def get_all_users(self) -> List[DomainUser]:
        """Get all users from database."""
        return await self.user_repo.get_all_users()

    async def get_all_roles(self) -> List[DomainRole]:
        """Get all roles from database."""
        return await self.role_repo.get_all_roles()

    async def update_user_role(self, user_id: UUID4, role_name: str) -> DomainUser:
        """Update user role by user_id."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There is no such user with given user_id.",
            )

        existing_role = await self.role_repo.get_by_name(role_name)
        if not existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="There is no such role with given role_name. Try to create it firts.",
            )

        user.role = role_name
        updated_user = await self.user_repo.update(user)

        return updated_user

    async def create_new_role(self, role_create: RoleCreate) -> DomainRole:
        """Create new custom role."""
        existing_role = await self.role_repo.get_by_name(role_create.name)
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists"
            )

        new_role = DomainRole(
            id=uuid.uuid4(),
            name=role_create.name,
            permissions=role_create.permissions
        )

        created_role = await self.role_repo.create(new_role)
        if not created_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Error creating a new role"
            )

        return created_role
