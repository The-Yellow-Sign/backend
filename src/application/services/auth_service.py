import uuid

from fastapi import HTTPException, status

from src.api.schemas.auth import UserRegistration
from src.domain.models.user import User as DomainUser
from src.domain.repositories.user_repo import IUserRepository
from src.infrastructure.security.jwt import create_access_token
from src.infrastructure.security.password import get_password_hash, verify_password


class AuthService:

    """Provides method for authentification."""

    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo

    async def register_new_user(self, user_registration: UserRegistration) -> DomainUser:
        """Register new user.

        1. Check that no user exists with the same email or username
        2. Hash the password
        3. Save the user in db.
        """
        user_from_db = await self.user_repo.get_by_username(user_registration.username)
        if user_from_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username is already registered"
            )

        user_from_db = await self.user_repo.get_by_email(user_registration.email)
        if user_from_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered"
            )

        hashed_password = get_password_hash(user_registration.password)
        new_user = DomainUser(
            id=uuid.uuid4(),
            username=user_registration.username,
            email=user_registration.email,
            role="user",
            hashed_password=hashed_password,
        )

        created_user = await self.user_repo.create(new_user)
        if not created_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User could not be created (possible duplicate)",
            )

        return created_user

    async def authenticate_user(self, username: str, password: str) -> dict:
        """Authentificate user.

        1. Find user in database by username
        2. Check the password
        3. Generate JWT if everything is ok.
        """
        user = await self.user_repo.get_by_username(username)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = {"sub": str(user.id), "role": user.role}
        access_token = create_access_token(data=token_data)

        return {"access_token": access_token, "token_type": "bearer"}
