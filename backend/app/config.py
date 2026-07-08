import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Search for .env first in root directory, then backend directory
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="latin-1",
        extra="ignore"
    )

    DATABASE_URL: str = Field(default="postgresql://postgres:postgres@localhost:5432/artfolio_db")
    JWT_SECRET_KEY: str = Field(default="dev_secret_key_change_me_in_production")
    JWT_ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

settings = Settings()
