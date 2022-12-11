"""
Модуль содержит класс с брокером сообщений.

Архитектура Rabbit следующая:

Есть очередь, в которую попадают все вновь приходящие message — queue_waiting_depart.
Есть обменник для этой очереди — exchange_incoming.

По истечению expiration в очереди queue_waiting_depart message отправляются в сортирующий обменник — exchange_sorter.
В обменнике exchange_sorter message перенаправляются в очереди с одноименными названиями routing_key.
Иными словами сортировка такая: routing_key == queue_name

В этой очереди message дожидается пока её прочитает consumer.
Если consumer что-то не смог сделать с сообщением
(иными словами не сказал basic_ack) — message отправляется в обменник exchange_retry,
а от туда сразу в очередь queue_waiting_retry.

В очереди queue_waiting_retry установлен аргумент x-message-ttl,
по истечению этого времени message отправится назад в exchange_sorter и цикл повторится.

Соответственно на совести разработчика следить за кол-вом таких итераций и,
если их кол-во превысит max_retry_count — дропить message, уведомляя об этом из логгера.
"""
import asyncio
from typing import Optional, Union, Callable

import aio_pika
from aio_pika import Message, DeliveryMode, ExchangeType
from aio_pika.abc import AbstractRobustConnection, AbstractChannel, AbstractQueue
from pamqp.commands import Basic
from pydantic import SecretStr

from src.config.settings import config
from src.message_brokers.abstract_classes import AbstractMessageBroker
from src.utils.timeout_limiter import timeout_limiter


class RabbitMessageBroker(AbstractMessageBroker):

    """Класс с интерфейсом брокера сообщений RabbitMQ."""

    def __init__(self, host: str, port: int, login: SecretStr, password: SecretStr) -> None:
        """
        Конструктор.

        Args:
            host: хост
            port: порт
            login: логин
            password: пароль
        """
        self.host = host
        self.port = port
        self.login = login
        self.password = password

    @timeout_limiter(max_timeout=config.rabbit.max_timeout, logger_name='message_brokers.consume')
    async def consume(self, queue_name: str, callback: Callable) -> None:
        """
        Метод обрабатывает сообщения функцией callback из очереди с названием queue_name.
        Callback-и выполняются асинхронно (быстро, параллельно, для I/O задач).

        Args:
            queue_name: название очереди, из которой хотим получить данные
            callback: функция, которая будет обрабатывать сообщения
        """
        connection = await self._get_connect()
        async with connection:
            running_loop = asyncio.get_running_loop()
            channel = await connection.channel()
            queue = await self._create_alive_queue(queue_name=queue_name, channel=channel)
            iterator = queue.iterator()

            async with iterator:
                async for message in iterator:

                    # Выключаем consumer и удаляем одноразовую очередь по kill_signal.
                    if message.body == config.rabbit.kill_signal:
                        await self._kill_alive_queue(queue_name=queue_name, channel=channel)
                        break

                    running_loop.create_task(callback(message))

    @timeout_limiter(max_timeout=config.rabbit.max_timeout, logger_name='message_brokers.publish')
    async def publish(
        self,
        message_body: bytes,
        queue_name: str,
        message_headers: Optional[dict] = None,
        delay: Union[int, float] = 0
    ) -> bool:
        """
        Метод складывает сообщение в очередь.

        Args:
            message_body: содержимое сообщения
            delay: ttl сообщения, указывается в секундах (сколько секунд подождать прежде, чем отправить)
            queue_name: название очереди, в которую нужно отправить сообщение
            message_headers: заголовок сообщения (сюда нужно вставить x-request-id)

        Returns:
            Вернёт ответ на вопрос была ли запись успешно добавлена
        """
        connection = await self._get_connect()
        async with connection:
            channel = await connection.channel()

            exchange_incoming = await channel.declare_exchange(
                name=config.rabbit.exchange_incoming,
                type=ExchangeType.FANOUT,
                durable=True
            )

            message = Message(
                headers=message_headers or {},
                body=message_body,
                delivery_mode=DeliveryMode.PERSISTENT,
                expiration=delay
            )

            await self._create_alive_queue(queue_name=queue_name, channel=channel)
            result = await exchange_incoming.publish(message=message, routing_key=queue_name)
            return isinstance(result, Basic.Ack)

    @timeout_limiter(max_timeout=config.rabbit.max_timeout, logger_name='message_brokers.idempotency_startup')
    async def idempotency_startup(self) -> None:
        """
        Метод для конфигурации базовой архитектуры RabbitMQ.
        Использовать ОДИН раз при старте сервиса.

        Можно конечно и больше,
        но этот метод все действие выполнит только один раз,
        следовательно, никакого резона вызывать его более одного раза нет.
        """
        connection = await self._get_connect()
        async with connection:
            channel = await connection.channel()

            # Обменник, принимающий все входящие в rabbit сообщения.
            exchange_incoming = await channel.declare_exchange(
                name=config.rabbit.exchange_incoming,
                type=ExchangeType.FANOUT,
                durable=True
            )

            # Обменник, сортирующий сообщения и распределяющий их в нужные «живые» очереди, исходя из routing_key.
            exchange_sorter = await channel.declare_exchange(  # noqa: F841
                name=config.rabbit.exchange_sorter,
                type=ExchangeType.DIRECT,
                durable=True
            )

            # Обменник, доставляющий сообщения во временное хранилище,
            # если попытка что-то сделать с сообщением не удалась.
            exchange_retry = await channel.declare_exchange(
                name=config.rabbit.exchange_retry,
                type=ExchangeType.FANOUT,
                durable=True
            )

            # Базовая очередь, в которую будут поступать все сообщения.
            # По истечению ttl (может быть и ttl=0) отправляет сообщения в соответствующую routing_key очередь.
            # С помощью такой архитектуры мы можем создавать отложенные сообщения,
            # не прибегая к дополнительным инструментам (консистентно).
            queue_waiting_depart = await channel.declare_queue(
                name=config.rabbit.queue_waiting_depart,
                durable=True,
                arguments={
                    'x-dead-letter-exchange': config.rabbit.exchange_sorter
                }
            )

            # Очередь, где будут храниться все сообщения, которые не удалось обработать.
            # Они будут лежать в очереди определённое время (x-message-ttl).
            # По истечению этого времени будет вновь попытка отправить сообщение в «живую» очередь.
            queue_waiting_retry = await channel.declare_queue(
                name=config.rabbit.queue_waiting_retry,
                durable=True,
                arguments={
                    'x-dead-letter-exchange': config.rabbit.exchange_sorter,
                    'x-message-ttl': config.rabbit.default_message_ttl_ms
                }
            )
            await queue_waiting_depart.bind(exchange_incoming)
            await queue_waiting_retry.bind(exchange_retry)

    async def _create_alive_queue(self, queue_name: str, channel: AbstractChannel) -> AbstractQueue:
        """
        Внутренний метод для создания «живой» очереди и привязки её к сортирующему обменнику.

        Под живой очередью мы понимаем очередь, из которой consumer будет читать данные.

        Args:
            queue_name: название очереди
            channel: канал

        Returns:
            Вернёт созданную очередь и обменник.
        """

        queue = await channel.declare_queue(
            name=queue_name,
            durable=True,
            arguments={
                'x-dead-letter-exchange': config.rabbit.exchange_retry
            }
        )
        await queue.bind(config.rabbit.exchange_sorter, routing_key=queue_name)
        return queue

    async def _kill_alive_queue(self, queue_name: str, channel: AbstractChannel) -> None:
        """
        Внутренний метод для удаления «живой» очереди.

        Args:
            queue_name: название очереди
            channel: канал
        """
        await channel.queue_delete(queue_name=queue_name)

    async def _get_connect(self) -> AbstractRobustConnection:
        """
        Внутренний метод класса (нужен для создания соединения).

        Returns:
            Вернёт соединение с БД.
        """
        return await aio_pika.connect_robust(
            host=self.host,
            port=self.port,
            login=self.login.get_secret_value(),
            password=self.password.get_secret_value()
        )


message_broker_factory = RabbitMessageBroker(
    host=config.rabbit.host,
    port=config.rabbit.port,
    login=config.rabbit.login,
    password=config.rabbit.password
)


async def get_message_broker() -> AbstractMessageBroker:
    """Функция возвращает объект message_broker."""
    return message_broker_factory
