FROM python:3.11.7-alpine3.19

ENV POETRY_VERSION=1.8.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VENV=/opt/poetry-venv \
    POETRY_CACHE_DIR=/opt/.cache

RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}


ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

COPY ../poetry.lock pyproject.toml ./
COPY README.md ./
COPY . .

RUN poetry lock && \
    poetry install --no-interaction --no-cache --no-root

COPY scheduler/ scheduler/
COPY bot/services/ bot/services/
COPY bot/database/ bot/database/
COPY bot/core/ bot/core/
COPY bot/image_generator/ bot/image_generator/

# Run the application using poetry
CMD ["poetry", "run", "python", "-m", "scheduler.main"]
