from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    """Project settings."""

    PROJECT_NAME: str = "GitLab Semantic Search API"
    VERSION: str = "0.1.0"

    DATABASE_URL: SecretStr

    SECRET_KEY: SecretStr
    ENCRYPTION_KEY: SecretStr
    MLOPS_SERVICE_URL: SecretStr
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
