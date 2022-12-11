# type: ignore
"""Модуль содержит функцию для обработки сообщения."""
import logging

from aio_pika.abc import AbstractIncomingMessage

from src.config.settings import config
from src.message_brokers.rabbit_message_broker import message_broker_factory
from src.worker.models.log import log_names
from src.worker.models.message_data import MessageData


async def callback(message: AbstractIncomingMessage) -> None:  # noqa: WPS231,WPS212,WPS213
    """
    Функция для обработки каждого сообщения из очереди.

    Обратите внимание, что мы вручную управляем состоянием сообщения пользуясь ack, reject и т.д.
    Подробнее см.
    https://www.rabbitmq.com/confirms.html

    Args:
        message: сообщение, приходящее из очереди
    """
    header = message.info()
    message_data = MessageData(
        x_request_id=header,
        count_retry=header,
        text=message.body
    )

    if message_data.count_retry > config.rabbit.max_retry_count:
        logger.info(log_names.info.drop_message, 'Too many repeat inserts in the queue', message_data.x_request_id)
        return await message.ack()

    try:

        new_text = message_data.text[::-1].encode()
        await message_broker_factory.publish(
            message_body=new_text,
            queue_name=config.rabbit.websocket_queue
        )
        logger.info('message %s processed successfully', message_data.x_request_id)
        return await message.ack()

    except Exception as error:
        # При возникновении любой ошибки мы отправим сообщение повторно в очередь.
        logger.error(error)
        return await message.reject()


logger = logging.getLogger('worker_callback')
