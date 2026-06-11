from enum import Enum
from typing import Dict, Set

from src.domain.models.user import UserRole


class Action(str, Enum):

    """Data structure for actions in different services (for RBAC)."""

    CHAT_READ = "chat:read"
    CHAT_WRITE = "chat:write"
    CHAT_CREATE = "chat:create"

    REPO_READ = "repo:read"
    REPO_CONFIG = "repo:config" # initial config

    INDEXING_TRIGGER = "indexing:trigger"
    INDEXING_DELETE = "indexing:delete"
    INDEXING_UPDATE = "indexing:update"
    INDEXING_GET = "indexing:get"

    ADMIN_ACCESS = "admin:access" # for getting and changing values in db

ROLE_PERMISSIONS: Dict[UserRole, Set[Action]] = {
    UserRole.USER: {
        Action.CHAT_READ,
        Action.CHAT_WRITE,
        Action.CHAT_CREATE,
        Action.REPO_READ,
        Action.INDEXING_GET
    },
    UserRole.ADMIN: {
        Action.CHAT_READ,
        Action.CHAT_WRITE,
        Action.CHAT_CREATE,
        Action.REPO_READ,
        Action.REPO_CONFIG,
        Action.INDEXING_TRIGGER,
        Action.INDEXING_DELETE,
        Action.INDEXING_UPDATE,
        Action.INDEXING_GET,
        Action.ADMIN_ACCESS
    }
}
