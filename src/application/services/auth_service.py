from fastapi import HTTPException, status


class AuthService:

    """Provides method for authentification."""

    async def authenticate_user(self, username: str, password: str) -> dict:
        """Authentificate user.

        1. Find user in database by username
        2. Check the password
        3. Generate JWT if everything is ok.
        """
        is_correct_password = (password == "userpass") # noqa: S105
        is_admin = (username == "admin" and password == "adminpass") # noqa: S105

        if not is_correct_password and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if is_admin:
            token_content = "fake_admin_token" # noqa: S105
        else:
            token_content = f"fake_token_for_{username}" # noqa: S105

        return {"access_token": token_content, "token_type": "bearer"}
