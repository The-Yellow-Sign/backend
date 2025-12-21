import uuid
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.admin_service import AdminService
from src.application.services.auth_service import AuthService
from src.application.services.chat_service import ChatService
from src.application.services.index_service import IndexService
from src.domain.models.user import User as DomainUser
from src.domain.repositories.chat_repo import IChatRepository
from src.domain.repositories.gitlab_repo import IGitLabRepository
from src.domain.repositories.job_repo import IJobRepository
from src.domain.repositories.role_repo import IRoleRepository
from src.domain.repositories.user_repo import IUserRepository
from src.infrastructure.db.repositories.sqlalchemy_chat_repo import SqlAlchemyChatRepository
from src.infrastructure.db.repositories.sqlalchemy_gitlab_repo import SqlAlchemyGitLabRepository
from src.infrastructure.db.repositories.sqlalchemy_job_repo import SqlAlchemyJobRepository
from src.infrastructure.db.repositories.sqlalchemy_role_repo import SqlAlchemyRoleRepository
from src.infrastructure.db.repositories.sqlalchemy_user_repo import SqlAlchemyUserRepository
from src.infrastructure.db.session import get_db_session
from src.infrastructure.security.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")


def get_user_repository(db: AsyncSession = Depends(get_db_session)) -> IUserRepository:
    """Get user's repository."""
    return SqlAlchemyUserRepository(session=db)


def get_auth_service(user_repo: IUserRepository = Depends(get_user_repository)) -> AuthService:
    """Get auth service."""
    return AuthService(user_repo=user_repo)


def get_chat_repository(db: AsyncSession = Depends(get_db_session)) -> IChatRepository:
    """Get chat's repository."""
    return SqlAlchemyChatRepository(session=db)


def get_chat_service(chat_repo: IUserRepository = Depends(get_chat_repository)) -> ChatService:
    """Get chat's service."""
    return ChatService(chat_repo=chat_repo)


def get_role_repository(db: AsyncSession = Depends(get_db_session)) -> IRoleRepository:
    """Get roles' repository."""
    return SqlAlchemyRoleRepository(session=db)


def get_gitlab_repository(db: AsyncSession = Depends(get_db_session)) -> IGitLabRepository:
    """Get GitLab's repository."""
    return SqlAlchemyGitLabRepository(session=db)


def get_job_service(db: AsyncSession = Depends(get_db_session)) -> IJobRepository:
    """Get job service."""
    return SqlAlchemyJobRepository(session=db)


def get_index_service(
    gitlab_repo: IGitLabRepository = Depends(get_gitlab_repository),
    job_repo: IJobRepository = Depends(get_job_service)
) -> IndexService:
    """Get index service."""
    return IndexService(gitlab_repo=gitlab_repo, job_repo=job_repo)


def get_admin_service(
    user_repo: IUserRepository = Depends(get_user_repository),
    role_repo: IRoleRepository = Depends(get_role_repository),
) -> AdminService:
    """Get admin service."""
    return AdminService(user_repo=user_repo, role_repo=role_repo)


async def get_current_user(
    token: str = Depends(oauth2_scheme), user_repo: IUserRepository = Depends(get_user_repository)
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
