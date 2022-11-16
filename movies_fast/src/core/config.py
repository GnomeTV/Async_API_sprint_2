import os
from logging import config as logging_config

from core.logger import LOGGING
from pydantic import BaseSettings, Field

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)


class Settings(BaseSettings):
    # Название проекта используется в Swagger-документации
    project_name: str = "movies"
    # Настройки Redis
    redis_host: str = "127.0.0.1"
    redis_port: int = 6379
    # Настройки Elasticsearch
    elastic_host: str = "127.0.0.1"
    elastic_port: int = 9200

    class Config:
        """Настройки настроек."""

        env_file = "../../.env"
        env_file_encoding = "utf-8"


settings = Settings()

# Корень проекта
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
