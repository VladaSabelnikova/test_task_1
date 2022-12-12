# Докер файл с Worker-ом.
FROM python:3.9.5-slim

COPY pyproject.toml .
RUN pip install --upgrade pip && pip install poetry
ENV POETRY_VIRTUALENVS_CREATE false
RUN poetry install --no-dev

COPY .env .

WORKDIR ./src

COPY src/__init__.py .
COPY src/config ./config
COPY src/message_brokers ./message_brokers
COPY src/utils ./utils
COPY src/worker ./worker

WORKDIR /

ENV PYTHONPATH "${PYTHONPATH}:${PWD}"

CMD poetry run python src/worker/main.py
