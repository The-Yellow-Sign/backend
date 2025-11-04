from typing import List
from fastapi import APIRouter, Depends, status

from src.api.dependencies import get_current_admin_user
from src.api.schemas.admin import RoleCreate, UserResponse, UserRoleUpdate


router_admin = APIRouter(
    dependencies=[Depends(get_current_admin_user)]
)

@router_admin.get("/users", response_model=List[UserResponse])
async def get_all_users():
    ...

@router_admin.put("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(user_id: int, role_update: UserRoleUpdate):
    ...

@router_admin.post("/roles", status_code=status.HTTP_201_CREATED)
async def create_new_role(role: RoleCreate):
    ...
