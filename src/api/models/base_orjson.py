"""Модуль содержит базовый класс."""
from typing import Any

import orjson
from pydantic import BaseModel


def orjson_dumps(v: Any, *, default: Any) -> str:
    """Быстрый orjson.dumps."""
    return orjson.dumps(v, default=default).decode()


class BaseOrjson(BaseModel):

    """Базовый класс с быстрой сериализацией в json."""

    class Config:

        """
        Настройки pydantic.
        Подробнее см.
        https://pydantic-docs.helpmanual.io/usage/model_config/
        """

        allow_population_by_field_name = True
        validate_assignment = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps
