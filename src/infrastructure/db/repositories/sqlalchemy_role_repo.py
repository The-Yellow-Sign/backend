from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.models.user import Role as DomainRole
from src.domain.repositories.role_repo import IRoleRepository
from src.infrastructure.db.models import Role as ORMRole


class SqlAlchemyRoleRepository(IRoleRepository):

    """Roles' repository realisation for SQLAlchemy."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, role: DomainRole) -> Optional[DomainRole]:
        """Create new role and put it in db."""
        orm_role = ORMRole(name=role.name, permissions=role.permissions)
        self.session.add(orm_role)
        try:
            await self.session.flush()
            await self.session.refresh(orm_role)
        except IntegrityError:
            await self.session.rollback()
            return None

        return DomainRole.model_validate(orm_role)

    async def get_by_name(self, role_name: str) -> Optional[DomainRole]:
        """Get info about role by its name."""
        stmt = select(ORMRole).where(ORMRole.name == role_name)
        result = await self.session.execute(stmt)
        orm_role = result.scalar_one_or_none()

        if orm_role:
            return DomainRole.model_validate(orm_role)
        return None

    async def get_all_roles(self) -> List[DomainRole]:
        """Get list of all existing roles."""
        stmt = select(ORMRole)
        result = await self.session.execute(stmt)
        orm_roles = result.scalars().all()

        return [DomainRole.model_validate(orm_role) for orm_role in orm_roles]
