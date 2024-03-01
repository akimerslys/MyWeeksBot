FROM python:3.11.7-alpine3.19 as python-base

ENV POETRY_VERSION=1.8.1 \
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
COPY ../poetry.lock pyproject.toml ./
COPY README.md ./

RUN poetry check && \
    poetry install --no-interaction --no-cache --no-root
COPY . .
CMD ["poetry", "run", "python", "-m", "bot.main"]
