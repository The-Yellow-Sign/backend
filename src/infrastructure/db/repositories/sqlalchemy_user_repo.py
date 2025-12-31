from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.user import User as DomainUser
from src.domain.repositories.user_repo import IUserRepository
from src.infrastructure.db.models import User as ORMUser


class SqlAlchemyUserRepository(IUserRepository):

    """User's repository realisation for SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _transform_orm_model_to_domain(self, orm_model: ORMUser) -> DomainUser:
        return DomainUser(
            id=orm_model.id,
            username=orm_model.username,
            email=orm_model.email,
            role=orm_model.role,
            hashed_password=orm_model.hashed_password
        )

    async def get_all_users(self) -> List[DomainUser]:
        """Retrieve all existing users from db."""
        stmt = select(ORMUser)
        result = await self.session.execute(stmt)
        orm_users = result.scalars().all()

        return [self._transform_orm_model_to_domain(orm_user) for orm_user in orm_users]

    async def get_by_username(self, username: str) -> Optional[DomainUser]:
        """Retrieve user from db by id."""
        stmt = select(ORMUser).where(ORMUser.username == username)
        result = await self.session.execute(stmt)
        orm_user = result.scalar_one_or_none()

        if orm_user:
            return self._transform_orm_model_to_domain(orm_user)
        return None

    async def get_by_email(self, email: str) -> Optional[DomainUser]:
        """Retrieve user from db by email adress."""
        stmt = select(ORMUser).where(ORMUser.email == email)
        result = await self.session.execute(stmt)
        orm_user = result.scalar_one_or_none()

        if orm_user:
            return self._transform_orm_model_to_domain(orm_user)
        return None

    async def get_by_id(self, user_id: UUID) -> Optional[DomainUser]:
        """Retrieve user from db by username."""
        stmt = select(ORMUser).where(ORMUser.id == user_id)
        result = await self.session.execute(stmt)
        orm_user = result.scalar_one_or_none()

        if orm_user:
            return self._transform_orm_model_to_domain(orm_user)
        return None

    async def create(self, user: DomainUser) -> DomainUser:
        """Create new user and put them in db."""
        db_user = ORMUser(
            username=user.username,
            email=user.email,
            role=user.role,
            hashed_password=user.hashed_password,
        )

        self.session.add(db_user)
        try:
            await self.session.flush()
            await self.session.refresh(db_user)
        except IntegrityError:
            await self.session.rollback()
            return None

        return self._transform_orm_model_to_domain(db_user)

    async def update(self, user: DomainUser) -> Optional[DomainUser]:
        """Update info about existing user."""
        stmt = select(ORMUser).where(ORMUser.id == user.id)
        result = await self.session.execute(stmt)
        orm_user = result.scalar_one_or_none()
        if not orm_user:
            return None

        orm_user.update_from_domain(user)

        try:
            await self.session.flush()
            await self.session.refresh(orm_user)
        except IntegrityError:
            await self.session.rollback()
            return None

        return self._transform_orm_model_to_domain(orm_user)
