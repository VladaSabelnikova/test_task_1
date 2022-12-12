# Тестовая задача вариант 2

### Собрала код в контейнеры

### Инструкция по развёртыванию:
1. Клонировать проект
2. В корне проекта создать .env файл (образец в .env_example)
3. Установить зависимости `poetry install`
4. Запустить сервисы `docker-compose up -d`

После этого создать в Postman соединение с Websocket ws://localhost:8001/listen_results
https://blog.postman.com/postman-supports-websocket-apis/

И запустить src/api/ddos_script.py

## PS:
Артём сообщил мне, что в работе «_сделано много лишнего_» и это минус.

Вот уж не думала, что в тестовом задании, суть которого в демонстрации навыков, best practices могут быть ЛИШНИМИ! :)

Хочу пояснить своё решение:


В работе я привыкла опираться не только на ТЗ, но и на best practices, даже если заказчик об этом не просит.
Я всегда исхожу из того, что мой код должен решить те проблемы, о которых заказчик еще не знает.

Rate-limiter, логгирование в json (для последующей агрегации), 
JWT авторизация и другие использованные технологии на мой взгляд являются must have для любого API.
