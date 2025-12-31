from typing import List

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, status

from src.api.dependencies import get_current_admin_user
from src.api.schemas.repository import (
    GitLabConfigCreate,
    Repository,
)
from src.application.services.index_service import IndexService

router_repository = APIRouter(
    dependencies=[Depends(get_current_admin_user)],
    route_class=DishkaRoute
)


@router_repository.post("/config", status_code=status.HTTP_202_ACCEPTED)
async def configure_gitlab(
    config_data: GitLabConfigCreate,
    service: FromDishka[IndexService]
):
    """Save GitLab instans' link and private token."""
    return await service.configure_gitlab(
        url=str(config_data.url),
        private_token=config_data.private_token
    )


@router_repository.get("/list", response_model=List[Repository])
async def list_gitlab_repositories(
    service: FromDishka[IndexService]
):
    """Get list of repositories that are available for indexing."""
    return await service.list_repositories()
