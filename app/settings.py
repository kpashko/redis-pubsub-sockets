import os

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class RedisSettingsMixin(BaseSettings):
    redis_url: str
    worker_list_key: str
    cache_key: str
    task_key: str
    task_queue: str


class DBSettingsMixin(BaseSettings):
    sqlalchemy_database_url: PostgresDsn
    sqlalchemy_async_engine_url: PostgresDsn


class Settings(
    DBSettingsMixin,
    RedisSettingsMixin,
):
    class Config:
        extra = "allow"
        env_file = '.env'

    access_token_expire_minutes: int
    jwt_secret_key: str


settings = Settings()
