"""Модуль содержит callback для RabbitMessageBroker, используемый в websocket."""
from typing import Callable

from aio_pika.abc import AbstractIncomingMessage
from fastapi import WebSocket


def callback(websocket: WebSocket) -> Callable:
    """
    Замыкание для передачи объекта websocket в callback брокера сообщений .

    Args:
        websocket: объект websocket

    Returns:
        Функцию callback для RabbitMessageBroker.
    """

    async def inner(message: AbstractIncomingMessage) -> None:
        """
        Callback брокера.

        Args:
            message: сообщение из Rabbit
        """
        await websocket.send_text(f'{message.body.decode()}')  # noqa: WPS237
        await message.ack()

    return inner


async def get_callback() -> Callable:
    """Функция вернёт объект колбэка."""
    return callback
