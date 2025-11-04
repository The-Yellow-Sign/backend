from fastapi import HTTPException, status


class AuthService:
    async def authenticate_user(self, username: str, password: str) -> dict:
        is_correct_password = (password == "userpass")
        is_admin = (username == "admin" and password == "adminpass")

        if not is_correct_password and not is_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if is_admin:
            token_content = "fake_admin_token" 
        else:
            token_content = f"fake_token_for_{username}"

        return {"access_token": token_content, "token_type": "bearer"}
