FROM python:3.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app/

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /uvx /bin/

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Compile bytecode
ENV UV_COMPILE_BYTECODE=1

# uv Cache
ENV UV_LINK_MODE=copy

# Install dependencies
COPY ./pyproject.toml ./uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project

ENV PYTHONPATH=/app

COPY . /app/

# Sync the project (if needed for any changes after initial install)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 