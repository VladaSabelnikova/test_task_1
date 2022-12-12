# Тестовая задача

Насколько я поняла ТЗ сделать нужно было следующее:
1. API с endpoint-ом /queue_reverse_text?text=...
2. RabbitMQ, куда с API попадает text
3. Worker, который слушает очередь и инвертирует text, после чего кладёт в другую очередь
4. Websocket, который случает очередь и показывает результат выполнения worker-а

Задача показалась мне несколько вырожденной, поэтому я добавила:
1. К endpoint-у API rate-limiter, для ограничения кол-ва запросов в минуту (src/api/utils/rate_limiter.py)
2. Обязательные поля Authorization и X-Request-Id в заголовке endpoint-а
3. DLX архитектуру очереди RabbitMQ (scheme/architecture_rabbit_mq.puml)
4. CI GitHub Actions .github/workflows

Я увлеклась и не успела по ТЗ сделать docker контейнеры для своих сервисов.
Если прямо нужно, то я сделаю, но сегодня и завтра у меня плотные дни.

### Инструкция по развёртыванию:
1. Клонировать проект
2. Установить зависимости `poetry install`
3. Запустить Redis и RabbitMQ `docker-compose up -d`
4. В папке src/api создать .env файл (образец в src/api/.env_example)
5. В папке src/websocket создать .env файл (образец в src/websocket/.env_example)
6. В папке src/worker создать .env файл (образец в src/worker/.env_example)
7. Запустить API (src/api/main.py)
8. Запустить Worker (src/worker/main.py)
9. Запустить Websocket (src/websocket/main.py)

После этого создать в Postman соединение с Websocket ws://localhost:8001/listen_results
https://blog.postman.com/postman-supports-websocket-apis/

И запустить src/api/ddos_script.py

PS:
Обратите внимание, что из-за созданного rate-limiter-а вы не сможете отправлять запросы больше api__rate_limit раз.
В противном случае API вернёт 429 ошибку.
