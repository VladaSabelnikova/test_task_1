"""Модуль содержит API с websocket-ом."""
from typing import Callable

import uvicorn
from fastapi import FastAPI, Depends
from starlette.websockets import WebSocket

from src.config.logging_settings import LOGGING
from src.config.settings import config
from src.message_brokers.abstract_classes import AbstractMessageBroker
from src.message_brokers.rabbit_message_broker import get_message_broker
from src.websocket.callback import get_callback
from src.websocket.startup import startup

app = FastAPI(
    on_startup=[
        startup
    ],
    openapi_url='/openapi.json',
    docs_url='/openapi'
)


@app.websocket('/listen_results')
async def websocket_endpoint(
    websocket: WebSocket,
    message_broker: AbstractMessageBroker = Depends(get_message_broker),
    callback: Callable = Depends(get_callback)
) -> None:
    """
    Роут для вывода результатов обработки сообщений.

    Args:
        websocket: объект websocket
        message_broker: брокер сообщений для чтения прогресса конвертации из очереди
        callback: обработчик сообщений
    """
    await websocket.accept()
    await message_broker.consume(config.rabbit.websocket_queue, callback=callback(websocket))


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=config.ws.host,
        port=config.ws.port,
        log_config=LOGGING,
    )
