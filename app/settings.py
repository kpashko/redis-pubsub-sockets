from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = '.env'

    sqlalchemy_database_url: PostgresDsn


settings = Settings()
