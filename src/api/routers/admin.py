from typing import List

from fastapi import APIRouter, Depends, status

from src.api.dependencies import get_admin_service, get_current_admin_user
from src.api.schemas.admin import RoleCreate, RoleResponse, UserResponse, UserRoleUpdate
from src.application.services.admin_service import AdminService

router_admin = APIRouter(dependencies=[Depends(get_current_admin_user)])


@router_admin.get("/users", response_model=List[UserResponse])
async def get_all_users(admin_service: AdminService = Depends(get_admin_service)):
    """Get all users from database."""
    return await admin_service.get_all_users()


@router_admin.get("/roles", response_model=List[RoleResponse])
async def get_all_roles(admin_service: AdminService = Depends(get_admin_service)):
    """Get all roles from database."""
    return await admin_service.get_all_roles()


@router_admin.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Update user role."""
    return await admin_service.update_user_role(user_id, role_update.role)


@router_admin.post("/roles", status_code=status.HTTP_201_CREATED)
async def create_new_role(
    role_create: RoleCreate, admin_service: AdminService = Depends(get_admin_service)
):
    """Create new custom role."""
    return await admin_service.create_new_role(role_create)
