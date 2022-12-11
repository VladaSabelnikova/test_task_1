"""Модуль содержит настройки для RabbitMQ."""

from pydantic import BaseSettings, SecretStr


class RabbitSettings(BaseSettings):

    """Настройки RabbitMQ."""

    host: str
    port: int
    login: SecretStr
    password: SecretStr
    queue_waiting_depart: str
    queue_waiting_retry: str
    exchange_incoming: str
    exchange_sorter: str
    exchange_retry: str
    default_message_ttl_ms: int
    max_retry_count: int
    kill_signal: bytes
    queue_convert_tasks: str
    queue_progress_bar: str
    max_timeout: int

    class Config:
        """
        Настройки pydantic.
        Подробнее см.
        https://pydantic-docs.helpmanual.io/usage/model_config/
        """

        env_file = '.env'
        env_file_encoding = 'utf-8'


class Config(BaseSettings):

    """Класс с конфигурацией проекта."""

    rabbit: RabbitSettings = RabbitSettings()


config = Config()
