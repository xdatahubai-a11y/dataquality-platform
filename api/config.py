"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "DataQuality Platform"
    database_url: str = "sqlite:///./dataquality.db"
    spark_master: str = "local[*]"
    adls_account_name: str = ""
    adls_account_key: str = ""
    debug: bool = False

    model_config = {"env_prefix": "DQ_"}


settings = Settings()
