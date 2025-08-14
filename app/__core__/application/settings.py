from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic.fields import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Environment
    ENV: Literal["dev", "prod"] = Field(
        ...,
        description="Whether the application is running in development or production",
    )
    API_PORT: int = Field(..., description="The port the API will listen on")
    API_DEBUG: bool = Field(..., description="Whether the API will run in debug mode")

    # Application
    PAGINATION_PER_PAGE_LIMIT: int = Field(
        ...,
        description="The maximum number of items per page (global limit)",
    )
    PRODUCT_CATALOG_API_BASE_URL: str = Field(
        ...,
        description="The base URL of the product catalog API (global limit)",
    )
    PRODUCT_CATALOG_API_TIMEOUT_LIMIT: float = Field(
        ...,
        description="The timeout limit for requests to the product catalog API (global limit)",
    )
    PRODUCT_CATALOG_API_MAX_RETRIES: int = Field(
        ...,
        description="The maximum number of retries for requests to the product catalog API",
    )

    # Security
    API_KEY: str = Field(..., description="The API key for bypassing the JWT")
    JWT_SECRET_KEY: str = Field(..., description="The secret key for the JWT")
    JWT_EXPIRE_DAYS: int = Field(
        ..., description="The number of days the JWT will expire"
    )

    # Database
    DATABASE_DIALECT: str = Field(..., description="The dialect of the database")
    DATABASE_HOST: str = Field(..., description="The host of the database")
    DATABASE_PORT: int = Field(..., description="The port of the database")
    DATABASE_USER: str = Field(..., description="The user of the database")
    DATABASE_PASSWORD: str = Field(..., description="The password of the database")
    DATABASE_NAME: str = Field(..., description="The name of the database")
    DATABASE_POOL_SIZE: int = Field(..., description="The size of the database pool")

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        connection_string = f"{self.DATABASE_DIALECT}+psycopg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        if self.DATABASE_DIALECT == "postgresql" and self.ENV == "prod":
            return f"{connection_string}?sslmode=require"
        return connection_string


_settings = None


@lru_cache()
def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
