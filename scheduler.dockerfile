FROM python:3.11-alpine3.18

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_HOME="/etc/poetry" \
    POETRY_CACHE_DIR="/tmp/poetry_cache" \
    POETRY_VERSION=1.7.0

WORKDIR /usr/src/app


RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" \
    && poetry install --without admin --without dev --no-root \
    && pip uninstall -y poetry \
    && pybabel compile -d bot/locales \
    && rm -rf /home/appuser/.cache \
    && rm -rf $POETRY_CACHE_DIR \
    && rm -rf /usr/src/app/{__pycache__,admin} \
    && adduser -D appuser \
    && chown -R appuser:appuser .

USER appuser
COPY scheduler/main.py
COPY bot/services/
CMD ["arq", "bot.scheduler.main.WorkerSettings"]
