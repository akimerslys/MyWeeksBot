FROM python:3.11.8-alpine3.19 as python-base

ENV POETRY_VERSION=1.5.1 \
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

WORKDIR app
COPY poetry.lock .
COPY pyproject.toml .
COPY Makefile .

RUN poetry check && \
    poetry install --no-interaction --no-cache --no-root

COPY scheduler/ scheduler/
COPY bot/services/ bot/services/
COPY bot/database/ bot/database/
COPY bot/core/ bot/core/
COPY bot/image_generator/ bot/image_generator/

# Run the application using poetry
CMD ["make", "scheduler-run"]

