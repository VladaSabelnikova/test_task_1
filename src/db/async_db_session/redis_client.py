"""Модуль содержит сессию redis."""
from typing import Optional

import aioredis
from aioredis import Redis

from src.config.settings import config
from src.db.async_db_session.abstract_classes import AbstractDBSession


class AsyncRedisSession(AbstractDBSession):

    """Класс для работы с сессией Redis."""

    def __init__(self, host: str, port: int, db: int) -> None:
        """
        Конструктор.

        Args:
            host: хост
            port: порт
            db: БД
        """
        self.host = host
        self.port = port
        self.db = db
        self.connect: Optional[Redis] = None

    async def start(self) -> None:

        """Метод создаёт соединение."""

        self.connect = await aioredis.from_url(f'redis://{self.host}:{self.port}', db=self.db)  # noqa: WPS221

    async def stop(self) -> None:

        """Метод закрывает соединение."""

        await self.connect.close()  # type: ignore

    async def get_connect(self) -> Redis:
        """
        Метод возвращает соединение.

        Returns:
            Вернёт соединение с Redis.
        """
        return self.connect  # type: ignore


rate_limiter_client = AsyncRedisSession(
    host=config.redis.host,
    port=config.redis.port,
    db=config.redis.db_rate_limiter
)
