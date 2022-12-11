"""Модуль содержит функции, запускаемые при старте и остановке FastAPI."""
from src.db.async_db_session import redis_client


async def startup() -> None:

    """Функция, для действий во время старта приложения."""

    await redis_client.rate_limiter_client.start()


async def shutdown() -> None:

    """Функция, для действий во время завершения работы приложения."""

    await redis_client.rate_limiter_client.stop()
