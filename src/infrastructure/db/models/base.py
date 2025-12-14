import uuid
from typing import Annotated

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

uuidpk = Annotated[
    uuid.UUID,
    mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
]

class Base:

    """Base ORM-model model."""

    id: Mapped[uuidpk]


Base = declarative_base(cls=Base)
