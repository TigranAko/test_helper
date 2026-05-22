FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/usr/local/

COPY pyproject.toml uv.lock ./


RUN uv sync --no-dev --frozen

COPY . .


CMD ["python", "main.py"]
