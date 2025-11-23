from typing import Annotated

from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

intpk = Annotated[int, mapped_column(Integer, primary_key=True)]


class Base:

    """Base ORM-model model."""

    id: Mapped[intpk]


Base = declarative_base(cls=Base)
