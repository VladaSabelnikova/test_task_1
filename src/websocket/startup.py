"""Модуль содержит функции, запускаемые при старте и остановке FastAPI."""
from src.message_brokers.rabbit_message_broker import message_broker_factory


async def startup() -> None:

    """Функция, для действий во время старта приложения."""
    await message_broker_factory.idempotency_startup()
