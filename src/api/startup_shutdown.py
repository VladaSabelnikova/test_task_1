"""Модуль содержит функции, запускаемые при старте и остановке FastAPI."""
from src.db.async_db_session import redis_client
from src.message_brokers.rabbit_message_broker import message_broker_factory


async def startup() -> None:

    """Функция, для действий во время старта приложения."""

    await redis_client.rate_limiter_client.start()
    await message_broker_factory.idempotency_startup()


async def shutdown() -> None:

    """Функция, для действий во время завершения работы приложения."""

    await redis_client.rate_limiter_client.stop()
