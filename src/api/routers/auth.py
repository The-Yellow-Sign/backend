from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.api.dependencies import get_current_user
from src.api.schemas.auth import Token, UserResponse
from src.application.services.auth_service import AuthService
from src.domain.models.user import User

router = APIRouter()

def get_auth_service() -> AuthService:
    """Get AuthService instance."""
    return AuthService()


@router.post(
    "/token",
    response_model=Token,
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Authenticate user by login and password and return a JWT token."""
    token_data = await auth_service.authenticate_user(
        username=form_data.username,
        password=form_data.password
    )

    return Token(**token_data)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    """Get information about current user."""
    return current_user
