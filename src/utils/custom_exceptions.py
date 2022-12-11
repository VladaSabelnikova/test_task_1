"""Модуль содержит кастомные исключения."""


class ConnectionTimeoutError(Exception):

    """Класс с собственным исключением для работы с кешом и бд."""

    def __init__(
        self,
        source_name: str,
        message: str,
        error_type: str,
    ) -> None:
        """
        Конструктор.

        Args:
            source_name: название базы данных
            message: выводимое сообщение об ошибке
            error_type: само возникшее исключение
        """
        self.source_name = source_name
        self.message = message
        self.error_type = error_type

        super().__init__()

    def __str__(self) -> str:
        """Формат вывода сообщения."""
        return f'{self.source_name} | {self.message} {self.error_type}'
