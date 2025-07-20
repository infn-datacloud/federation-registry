ARG PYTHON_VERSION=3.12
ARG POETRY_VERSION=1.8.3

# Install packages using poetry
FROM ghcr.io/withlogicco/poetry:${POETRY_VERSION}-python-${PYTHON_VERSION}-slim AS builder

COPY ./pyproject.toml ./poetry.lock ./README.md /usr/src/app/
COPY ./fed_reg /usr/src/app/fed_reg

RUN poetry install --without dev

# Stage used in production with the service
FROM python:${PYTHON_VERSION}-slim AS production

ENV DEBIAN_FRONTEND=noninteractive
WORKDIR /app/

COPY --from=builder /usr/local/ /usr/local
COPY ./fed_reg ./fed_reg

CMD ["fastapi", "run", "/app/fed_reg/main.py", "--port", "80"]