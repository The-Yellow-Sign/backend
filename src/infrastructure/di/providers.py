import logging
from typing import AsyncIterable

from dishka import Provider, Scope, provide
from fastapi import HTTPException, status
from redis import ConnectionPool, Redis, asyncio as aioredis
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from src.application.services import AdminService, AuthService, ChatService, IndexService
from src.core.settings import Settings, settings
from src.domain.repositories import (
    IChatRepository,
    IGitLabRepository,
    IJobRepository,
    IRoleRepository,
    IUserRepository,
)
from src.domain.repositories.cache_repo import ICacheRepository
from src.infrastructure.cache.repositories.redis_cache_repo import RedisCacheRepository
from src.infrastructure.db.repositories import (
    SqlAlchemyChatRepository,
    SqlAlchemyGitLabRepository,
    SqlAlchemyJobRepository,
    SqlAlchemyRoleRepository,
    SqlAlchemyUserRepository,
)

logger = logging.getLogger(__name__)


class InfrastructureProvider(Provider):

    """Provider for core infrastructure components."""

    @provide(scope=Scope.APP)
    def get_settings(self) -> Settings:
        """Get project settings."""
        return settings

    @provide(scope=Scope.APP)
    def get_engine(self, settings: Settings) -> AsyncEngine:
        """Get AsyncEngine."""
        return create_async_engine(
            settings.DATABASE_URL.get_secret_value(),
            echo=False,
            pool_pre_ping=False
        )

    @provide(scope=Scope.REQUEST)
    async def get_session(self, engine: AsyncEngine) -> AsyncIterable[AsyncSession]:
        """Get database session."""
        async with AsyncSession(bind=engine, expire_on_commit=False) as session:
            try:
                yield session
                await session.commit()
            except SQLAlchemyError as sql_exc:
                await session.rollback()
                logger.error(f"SQLAlchemy error: {sql_exc}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Database error"
                ) from sql_exc
            except HTTPException as http_exc:
                await session.rollback()
                raise http_exc
            except Exception as e:
                await session.rollback()
                logger.error(f"Error: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal server error"
                ) from e


class RepositoryProvider(Provider):

    """Provider for Repositories."""

    scope = Scope.REQUEST

    @provide
    def get_user_repository(self, session: AsyncSession) -> IUserRepository:
        """Get user's repository."""
        return SqlAlchemyUserRepository(session=session)

    @provide
    def get_chat_repository(self, session: AsyncSession) -> IChatRepository:
        """Get chat's repository."""
        return SqlAlchemyChatRepository(session=session)

    @provide
    def get_role_repository(self, session: AsyncSession) -> IRoleRepository:
        """Get roles' repository."""
        return SqlAlchemyRoleRepository(session=session)

    @provide
    def get_gitlab_repository(self, session: AsyncSession) -> IGitLabRepository:
        """Get GitLab's repository."""
        return SqlAlchemyGitLabRepository(session=session)

    @provide
    def get_job_repository(self, session: AsyncSession) -> IJobRepository:
        """Get job service."""
        return SqlAlchemyJobRepository(session=session)


class SericeProvider(Provider):

    """Provider for Services."""

    scope = Scope.REQUEST

    @provide
    def get_auth_service(self, user_repo: IUserRepository) -> AuthService:
        """Get auth service."""
        return AuthService(user_repo=user_repo)

    @provide
    def get_chat_service(
        self,
        chat_repo: IChatRepository,
        cache_repo: ICacheRepository
    ) -> ChatService:
        """Get chat's service."""
        return ChatService(chat_repo=chat_repo, cache_repo=cache_repo)

    @provide
    def get_index_service(
        self,
        gitlab_repo: IGitLabRepository,
        job_repo: IJobRepository
    ) -> IndexService:
        """Get index service."""
        return IndexService(gitlab_repo=gitlab_repo, job_repo=job_repo)

    @provide
    def get_admin_service(
        self,
        user_repo: IUserRepository,
        role_repo: IRoleRepository,
    ) -> AdminService:
        """Get admin service."""
        return AdminService(user_repo=user_repo, role_repo=role_repo)


class CacheProvider(Provider):

    """Provider for cache."""

    @provide(scope=Scope.APP)
    def get_redis_pool(self) -> ConnectionPool:
        """Get Redis connection pool."""
        return aioredis.ConnectionPool.from_url(
            settings.REDIS_URL.get_secret_value(),
            decode_responses=True
        )

    @provide(scope=Scope.APP)
    async def get_redis_client(self, pool: ConnectionPool) -> AsyncIterable[Redis]:
        """Get Redis client."""
        client = aioredis.Redis(connection_pool=pool)
        try:
            yield client
        finally:
            await client.close()

    @provide(scope=Scope.REQUEST)
    async def get_cache_repository(
        self,
        client: Redis
    ) -> ICacheRepository:
        """Get Redis cache repository."""
        return RedisCacheRepository(client)
