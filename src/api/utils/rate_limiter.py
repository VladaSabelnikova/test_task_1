"""
Модуль содержит rate limiter.

Функция ограничивает кол-во запросов к endpoint-у в минуту.
Это нужно для защиты API от возможных DDOS атак.
"""
import datetime
from http import HTTPStatus as status
from typing import Callable

from aioredis import Redis
from fastapi import Depends, Header, HTTPException, Request

from src.db.async_db_session.redis_client import rate_limiter_client
from src.api.utils.payload_parser import parse_payload_from_token


def requests_per_minute(limiter: int) -> Callable:

    """
    Функция-замыкание.

    Она пробрасывает ограничение кол-ва запросов в минуту (limiter) в область видимости асинхронной функции inner.
    В свою очередь inner выполняет rate limiter.

    Args:
        limiter: ограничение кол-ва запросов в минуту

    Returns:
        Вернёт корутину, которую будут использовать ручки API в Depends (для ограничения к ним запросов).
    """

    async def inner(
        request: Request,
        redis_conn: Redis = Depends(rate_limiter_client.get_connect),
        authorization: str = Header(description='JWT token')
    ) -> None:
        """
        Функция для ограничения числа запросов в минуту.

        Args:
            request: запрос пользователя (из него нам нужен handle)
            redis_conn: соединение с Redis
            authorization: ключ в заголовке запроса (access токен пользователя)

        Raises:
            HTTPException:
                Если кол-во запросов превысило лимит
        """
        payload = await parse_payload_from_token(authorization)
        user_id = payload.user_id

        now = datetime.datetime.now()
        handle = request.url.path
        key = f'{handle}:{user_id}:{now.minute}'  # noqa: WPS237

        async with redis_conn.pipeline(transaction=True) as pipe:
            # Идемпотентно создаём запись в Redis-е.
            # Увеличиваем значение записи на 1.
            # Назначаем TTL записи в 59 секунд.
            result_from_redis = await (
                pipe.incr(name=key, amount=1).expire(name=key, time=59).execute()  # type: ignore  # noqa: WPS432
            )

        request_number = result_from_redis[0]  # Кол-во запросов пользователя к данному endpoint-у.

        if request_number > limiter:
            # Пользователь превысил лимит запросов к данному endpoint-у.
            raise HTTPException(detail=status.TOO_MANY_REQUESTS.phrase, status_code=status.TOO_MANY_REQUESTS.value)

    return inner
