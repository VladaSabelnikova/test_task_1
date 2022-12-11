"""Модуль содержит функцию для работы consumer-а."""
import asyncio
import logging

from src.config.settings import config
from src.message_brokers.rabbit_message_broker import message_broker_factory
from src.worker.callback import callback  # type: ignore


async def main() -> None:

    """Функция, запускающая consumer-а."""

    await message_broker_factory.idempotency_startup()

    logger.info('start worker')

    await message_broker_factory.consume(
        queue_name=config.rabbit.alive_queue,
        callback=callback
    )

logger = logging.getLogger('worker')

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
