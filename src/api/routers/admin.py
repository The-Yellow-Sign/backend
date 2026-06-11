from typing import List

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status
from pydantic import UUID4

from src.api.dependencies import PermissionChecker
from src.api.schemas.admin import RoleCreate, RoleResponse, UserResponse, UserRoleUpdate
from src.application.services.admin_service import AdminService
from src.core.security_policy import Action

router_admin = APIRouter(
    dependencies=[Depends(PermissionChecker(Action.ADMIN_ACCESS))],
    route_class=DishkaRoute
)


@router_admin.get(
    "/users",
    response_model=List[UserResponse]
)
async def get_all_users(admin_service: FromDishka[AdminService]):
    """Get all users from database."""
    return await admin_service.get_all_users()


@router_admin.get(
    "/roles",
    response_model=List[RoleResponse]
)
async def get_all_roles(admin_service: FromDishka[AdminService]):
    """Get all roles from database."""
    return await admin_service.get_all_roles()


@router_admin.put(
    "/users/{user_id}/role",
    response_model=UserResponse
)
async def update_user_role(
    user_id: UUID4,
    role_update: UserRoleUpdate,
    admin_service: FromDishka[AdminService],
):
    """Update user role."""
    return await admin_service.update_user_role(user_id, role_update.role)


@router_admin.post(
    "/roles",
    status_code=status.HTTP_201_CREATED
)
async def create_new_role(
    role_create: RoleCreate,
    admin_service: FromDishka[AdminService]
):
    """Create new custom role."""
    return await admin_service.create_new_role(role_create)
