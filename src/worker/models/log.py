"""Модуль содержит содержимое для логгеров в виде pydantic моделей."""
from src.worker.models.base_config import BaseConfig


class LogInfo(BaseConfig):

    """Уведомления."""

    drop_message: str = 'Dropped message because %s. X-Request-Id %s'


class LogNames(BaseConfig):

    """Все существующие названия вместе."""

    info: LogInfo = LogInfo()


log_names = LogNames()
