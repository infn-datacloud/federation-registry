ARG PYTHON_VERSION=3.10
ARG POETRY_VERSION=1.8.3

# Create requirements.txt from poetry dependencies
FROM ghcr.io/withlogicco/poetry:${POETRY_VERSION}-python-${PYTHON_VERSION}-slim AS requirements

WORKDIR /tmp

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes


# Stage used in production with no kubernetes
FROM tiangolo/uvicorn-gunicorn-fastapi:python${PYTHON_VERSION}-slim AS production

WORKDIR /app/

COPY --from=requirements /tmp/requirements.txt /app/requirements.txt

RUN apt-get update \
    && apt-get install -y git \
    && apt-get clean

RUN pip install --user --upgrade pip \
    && pip install --user --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./fed_reg /app/fed_reg

ENV PYTHONPATH=/app
ENV APP_MODULE=fed_reg.main:app
