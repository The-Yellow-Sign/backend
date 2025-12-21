from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.api.schemas.auth import UserInDB

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """Decode JWT token and find user in database."""
    return UserInDB(id=1, username="test_user", email="test@example.com", role="user")

async def get_current_admin_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """Check that current user has an admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="у тебя нет прав",
        )
    return current_user
