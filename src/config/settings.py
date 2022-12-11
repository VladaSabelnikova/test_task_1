"""Модуль содержит настройки различных сервисов."""
from pydantic import SecretStr, BaseModel

from src.config.base_config import BaseConfig


class RabbitSettings(BaseModel):

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
    max_timeout: int
    alive_queue: str
    websocket_queue: str


class RedisSettings(BaseModel):
    """Настройки Redis."""

    db_rate_limiter: int
    host: str
    port: int


class APISettings(BaseModel):

    """Настройки API."""

    host: str
    port: int
    rate_limit: int


class WebsocketSettings(BaseModel):

    """Настройки API с Websocket-ом."""

    host: str
    port: int


class Config(BaseConfig):

    """Настройки всех приложений."""

    redis: RedisSettings
    rabbit: RabbitSettings
    api: APISettings
    ws: WebsocketSettings


config = Config()
