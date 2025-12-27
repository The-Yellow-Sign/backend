import uuid
from typing import Optional

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.domain.models.user import User as DomainUser
from src.domain.repositories.user_repo import IUserRepository
from src.infrastructure.security.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")


@inject
async def get_current_user(
    user_repo: FromDishka[IUserRepository],
    token: str = Depends(oauth2_scheme),
) -> DomainUser:
    """Decode JWT token and find user in database."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id_str: Optional[str] = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError as error:
        raise credentials_exception from error

    user = await user_repo.get_by_id(user_id=user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_admin_user(
    current_user: DomainUser = Depends(get_current_user),
) -> DomainUser:
    """Check that current user has an admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role needed.",
        )
    return current_user
