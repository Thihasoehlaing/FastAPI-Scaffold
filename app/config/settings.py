from pydantic_settings import BaseSettings
from pydantic import Field, AnyHttpUrl
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "FastAPI"
    APP_ENV: str = "dev"
    APP_DEBUG: bool = True

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Auth
    JWT_SECRET: str
    JWT_EXPIRES_MIN: int = 60
    JWT_ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = Field(default_factory=list)

    # PostgreSQL (compose later if needed)
    PG_CONNECTION: str = "postgresql+psycopg"
    PG_HOST: str = "127.0.0.1"
    PG_PORT: int = 5432
    PG_DATABASE: str = "hospital"
    PG_USERNAME: str = "postgres"
    PG_PASSWORD: str = "secret"

    # Mongo (optional)
    MONGO_CONNECTION: str = "mongodb"
    MONGO_HOST: str = "127.0.0.1"
    MONGO_PORT: int = 27017
    MONGO_DATABASE: str = "hospital"
    MONGO_USERNAME: str = "god"
    MONGO_PASSWORD: str = "secret"

    # Storage
    STORAGE_DRIVER: str = "local"
    LOCAL_UPLOAD_DIR: str = "./storage/uploads"
    PUBLIC_BASE_URL: str = "http://localhost:8000/static"

    S3_BUCKET: str | None = None
    S3_REGION: str | None = None
    S3_ACCESS_KEY: str | None = None
    S3_SECRET_KEY: str | None = None
    S3_ENDPOINT_URL: str | None = None

    AZURE_BLOB_CONNECTION_STRING: str | None = None
    AZURE_CONTAINER: str | None = None

    MAX_UPLOAD_MB: int = 25
    ALLOWED_MIME: str = "image/jpeg,image/png,application/pdf"

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"{self.PG_CONNECTION}://{self.PG_USERNAME}:{self.PG_PASSWORD}"
            f"@{self.PG_HOST}:{self.PG_PORT}/{self.PG_DATABASE}"
        )

    @property
    def MONGO_URL(self) -> str:
        auth = f"{self.MONGO_USERNAME}:{self.MONGO_PASSWORD}@"
        return f"{self.MONGO_CONNECTION}://{auth}{self.MONGO_HOST}:{self.MONGO_PORT}/{self.MONGO_DATABASE}"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
