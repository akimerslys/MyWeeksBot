
FROM python:3.11.8-alpine3.19 as python-base

ENV POETRY_VERSION=1.8.2 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_HOME=/opt/poetry \
    POETRY_VENV=/opt/poetry-venv \
    POETRY_CACHE_DIR=/opt/.cache

    
FROM python-base as poetry-base

RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

FROM python-base as app

COPY --from=poetry-base ${POETRY_VENV} ${POETRY_VENV}

ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

COPY . .

RUN poetry check && \
    poetry install --no-interaction --no-cache --no-root && \
    apk add --no-cache make && \
    rm -rf home/bot/.cache && \
    rm -rf $POETRY_CACHE_DIR && \
    poetry run pybabel compile -d src/bot/locales

CMD ["poetry", "run", "make", "bot-run"]
#CMD ["sh", "poetry", "run", "python", "-m", "src.bot"]


