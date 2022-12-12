"""Модуль содержит Pydantic модели."""
from typing import Union, Optional

from pydantic import validator

from src.worker.models.base_config import BaseConfig  # type: ignore


class MessageData(BaseConfig):

    """Данные из очереди."""

    x_request_id: Union[str, dict]
    text: str
    count_retry: Union[int, dict]

    @validator('x_request_id')
    def x_request_id_to_str(cls, message: dict) -> Optional[str]:
        """
        Метод достаёт из словаря с заголовками нужный ключ.

        Args:
            message: сообщение

        Returns:
            Вернёт значение ключа.
        """
        return message['headers'].get('X-Request-Id', None)

    @validator('count_retry')
    def dict_to_int(cls, message: dict) -> int:
        """
        Метод достаёт из словаря с заголовками нужный ключ.

        Args:
            message: сообщение

        Returns:
            Вернёт count retry значение.
        """
        return message['headers']['x-death'][0]['count']
