FROM python:3.12-alpine

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

ENV UV_PYTHON_DOWNLOADS=never

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY main.py .

CMD ["uv", "run", "--no-sync", "main.py"]