"""Application configuration."""

import os
from importlib.metadata import version, PackageNotFoundError

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "DataQuality Platform"
    database_url: str = "sqlite:///./dataquality.db"
    spark_master: str = "local[*]"
    adls_account_name: str = ""
    adls_account_key: str = ""
    debug: bool = False
    cors_origins: str = "*"

    model_config = {"env_prefix": "DQ_"}

    @property
    def app_version(self) -> str:
        """Get application version from package metadata or environment."""
        try:
            return version("dataquality-platform")
        except PackageNotFoundError:
            return os.getenv("APP_VERSION", "dev")


settings = Settings()
