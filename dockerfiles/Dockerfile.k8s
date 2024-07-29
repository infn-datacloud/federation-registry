ARG PYTHON_VERSION=3.10
ARG POETRY_VERSION=1.8.3

FROM ghcr.io/withlogicco/poetry:${POETRY_VERSION}-python-${PYTHON_VERSION}-slim AS requirements

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

COPY ./pyproject.toml ./poetry.lock* ./
COPY ./fed_reg ./fed_reg

RUN poetry install --without dev

CMD ["fastapi", "run", "fed_reg/main.py", "--proxy-headers", "--port", "80"]
