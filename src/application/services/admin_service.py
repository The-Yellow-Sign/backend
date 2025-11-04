from typing import List

from fastapi import HTTPException, status

from src.domain.models.user import Role, User


class AdminService:
    async def get_all_users(self) -> List[User]:
        return [
            User(id=1, username="admin_user", email="admin@example.com", role="admin"),
            User(id=2, username="test_user", email="test@example.com", role="user"),
        ]

    async def update_user_role(self, user_id: int, role_name: str) -> User:
        if user_id == 2:
            return User(
                id=2,
                username="test_user",
                email="test@example.com",
                role=role_name
            )

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found or cannot be modified"
        )

    async def create_new_role(self, name: str, permissions: List[str]) -> Role:
        return Role(
            id=99,
            name=name,
            permissions=permissions
        )
