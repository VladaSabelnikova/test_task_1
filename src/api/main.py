"""Модуль содержит FastAPI приложение."""
import uvicorn
from fastapi import FastAPI, Depends, Header

from src.api.config.logging_settings import LOGGING
from src.api.startup_shutdown import startup, shutdown
from src.config.settings import config

from src.api.utils.rate_limiter import requests_per_minute
from src.message_brokers.rabbit_message_broker import message_broker_factory

app = FastAPI(
    on_startup=[
        startup
    ],
    on_shutdown=[
        shutdown
    ],
)


@app.post(
    '/queue_reverse_text',
    dependencies=[Depends(requests_per_minute(config.api.rate_limit))],
)
async def root(
    text: bytes,
    x_request_id: str = Header(),
) -> dict:
    """
    Endpoint отправляет заданный пользователем текст в брокер сообщений.

    Args:
        text: произвольный текст
        x_request_id: id запроса пользователя

    Returns:
        Вернёт ответ, или исключение 429, если кол-во запросов превысило лимит.
    """

    result = await message_broker_factory.publish(
        message_body=text,
        queue_name=config.rabbit.alive_queue,
        message_headers={'X-Request-Id': x_request_id}
    )
    return {'SUCCESS': result}


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=config.api.host,
        port=config.api.port,
        log_config=LOGGING,
    )
