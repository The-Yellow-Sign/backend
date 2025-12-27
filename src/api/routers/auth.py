from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.api.dependencies import get_current_user
from src.api.schemas.auth import Token, UserRegistration, UserResponse
from src.application.services.auth_service import AuthService
from src.domain.models.user import User

router = APIRouter(route_class=DishkaRoute)


@router.post(
    "/token",
    response_model=Token,
)
async def login_for_access_token(
    auth_service: FromDishka[AuthService],
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Authenticate user by login and password and return a JWT token."""
    token_data = await auth_service.authenticate_user(
        username=form_data.username, password=form_data.password
    )

    return Token(**token_data)


@router.post("/register", response_model=UserResponse)
async def register(
    user_create: UserRegistration, auth_service: FromDishka[AuthService]
):
    """Register new user."""
    created_user = await auth_service.register_new_user(user_create)
    return created_user


@router.get(
    "/me",
    response_model=UserResponse,
)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get information about current user."""
    return current_user
