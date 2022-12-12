# Докер файл с API.
FROM python:3.9.5-slim

EXPOSE 8000/tcp

COPY pyproject.toml .
RUN pip install --upgrade pip && pip install poetry
ENV POETRY_VIRTUALENVS_CREATE false
RUN poetry install --no-dev

COPY .env .

WORKDIR ./src

COPY src/__init__.py .
COPY src/config ./config
COPY src/db ./db
COPY src/message_brokers ./message_brokers
COPY src/utils ./utils
COPY src/api ./api

WORKDIR /

ENV PYTHONPATH "${PYTHONPATH}:${PWD}"

CMD poetry run python src/api/main.py
