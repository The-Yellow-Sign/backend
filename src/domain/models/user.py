from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID


@dataclass
class User:

    """Data structure for user information."""

    id: UUID
    username: str
    role: str
    hashed_password: str
    email: Optional[str] = None

@dataclass
class Role:

    """Data structure for role."""

    id: UUID
    name: str
    permissions: List[str]
