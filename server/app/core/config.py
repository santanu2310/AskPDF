from pathlib import Path
from typing import Literal
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

env_path = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_path, env_file_encoding="utf-8")

    API_KEY: str = ""
    API_ENDPOINT: str = ""

    # Google OAuth 2.0 Configuration
    GOOGLE_OAUTH2_CLIENT_ID: str = ""
    GOOGLE_OAUTH2_CLIENT_SECRET: str = ""
    GOOGLE_OAUTH2_PROJECT_ID: str = ""
    GOOGLE_OAUTH_REDIRECT_URI: str = "http://localhost:5174/auth/callback"

    # JWT Configuration
    JWT_ACCESS_SECRET_KEY: str = ""
    JWT_REFRESH_SECRET_KEY: str = ""
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # DB Configuration
    POSTGRES_USER: str = "devuser"
    POSTGRES_PWD: str = "devpass"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DATABASE: str = "askpdf"
    SQLALCHEMY_DEBUG: bool = False
    DATABASE_POOL_SIZE: int = 5
    DATABASE_POOL_RECYCLE_SECONDS: int = 600
    DATABASE_COMMAND_TIMEOUT_SECONDS: float = 30.0

    def get_postgres_dsn(self, driver: Literal["asyncpg", "psycopg2"]) -> str:
        return str(
            PostgresDsn.build(
                scheme=f"postgresql+{driver}",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PWD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DATABASE,
            )
        )


settings = Settings()
