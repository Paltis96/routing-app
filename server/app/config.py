from pydantic import BaseSettings
from functools import lru_cache
from typing import Dict

class Settings(BaseSettings):
    dsn: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()  # type: ignore
