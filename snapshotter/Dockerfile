FROM ghcr.io/astral-sh/uv:python3.12-trixie-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev

COPY alembic.ini ./
COPY src/ ./src/

RUN mkdir -p input output

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "src/main.py"]