from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    class Config:
        env_file = ".env"

    sqlalchemy_database_url: PostgresDsn
    sqlalchemy_async_engine_url: PostgresDsn

    access_token_expire_minutes: int
    jwt_secret_key: str

    worker_list_key: str
    task_queue: str


settings = Settings()
