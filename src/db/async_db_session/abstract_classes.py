"""Модуль содержит абстрактные классы."""
from abc import ABC, abstractmethod


class AbstractDBSession(ABC):
    """Абстрактный класс подключения к БД."""

    @abstractmethod
    async def start(self) -> None:
        """Метод создаёт соединение с БД."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Метод закрывает соединение с БД."""
        pass
