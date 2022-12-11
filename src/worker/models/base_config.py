# Flake8: noqa
# type: ignore
"""Модуль содержит базовый класс."""
from pydantic import BaseModel


class BaseConfig(BaseModel):

    """Базовый класс с настройками по умолчанию для всех моделей."""

    class Config:
        """
        Настройки pydantic.
        Подробнее см.
        https://pydantic-docs.helpmanual.io/usage/model_config/
        """
        validate_assignment = True
        arbitrary_types_allowed = True
