"""Модуль содержит базовые настройки для Pydantic модели."""
from pydantic import BaseSettings


class BaseConfig(BaseSettings):

    """Базовые настройки для Pydantic модели."""

    class Config:
        """
        Настройки pydantic.
        Подробнее см.
        https://pydantic-docs.helpmanual.io/usage/model_config/
        """

        env_file = '.env'
        env_file_encoding = 'utf-8'
        env_nested_delimiter = '__'
