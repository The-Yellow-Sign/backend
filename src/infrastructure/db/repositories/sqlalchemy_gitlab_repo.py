from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.knowledge import GitLabConfig as DomainGitLabConfig
from src.domain.repositories.gitlab_repo import IGitLabRepository
from src.infrastructure.db.models.gitlab import GitLabConfig as ORMGitLabConfig


class SqlAlchemyGitLabRepository(IGitLabRepository):

    """GitLab's repository realisation for SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _transform_orm_model_to_domain(
            self,
            orm_model: ORMGitLabConfig
    ) -> DomainGitLabConfig:
        return DomainGitLabConfig(
            id=orm_model.id,
            url=orm_model.url,
            private_token_encrypted=orm_model.private_token_encrypted
        )

    async def save_config(self, url: str, encrypted_token: str) -> DomainGitLabConfig:
        """Save or update the configuration.

        Use the singletone approach with id=1.
        If config with id=1 already exists then update it, otherwise create a new one.
        """
        stmt = select(ORMGitLabConfig).where(ORMGitLabConfig.id == 1)
        result = await self.session.execute(stmt)
        orm_gitlab_config = result.scalar_one_or_none()
        if not orm_gitlab_config:
            orm_gitlab_config = ORMGitLabConfig(
                id=1,
                url=url,
                private_token_encrypted=encrypted_token
            )
            self.session.add(orm_gitlab_config)
        else:
            orm_gitlab_config.url = url
            orm_gitlab_config.private_token_encrypted = encrypted_token

        config = self._transform_orm_model_to_domain(orm_gitlab_config)

        await self.session.flush()
        return config

    async def get_config(self) -> Optional[DomainGitLabConfig]:
        """Get current configuration."""
        stmt = select(ORMGitLabConfig).where(ORMGitLabConfig.id == 1)
        result = await self.session.execute(stmt)

        config = result.scalar_one_or_none()

        if config:
            return self._transform_orm_model_to_domain(config)
        return None
