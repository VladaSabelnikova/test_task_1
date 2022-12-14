# flake8: noqa
# type: ignore
"""Модуль содержит demo функцию для отправки запросов к API."""
from time import sleep

import httpx

from src.api.jwt_token import JWT_TOKEN


def main() -> None:

    """
    Функция отправляет запросы к API.

    Отправляем запросы с интервалом в 1.5 секунды и видим результат выполнения запроса.
    После превышения лимита запросов в минуту (rate_limit) API возвращает 429 Too Many Requests.
    После завершения текущей минуты можно вновь совершать запросы в пределах rate_limit.
    """

    url = 'http://localhost:8000/queue_reverse_text?text=vlada'
    headers = {'X-Request-Id': None, 'Authorization': JWT_TOKEN}

    for i in range(50):  # Пробуем DDOS-ить API.
        headers['X-Request-Id'] = str(i)
        response = httpx.post(url=url, headers=headers)
        print(response.status_code, response.text)
        sleep(1.5)


if __name__ == '__main__':
    main()
