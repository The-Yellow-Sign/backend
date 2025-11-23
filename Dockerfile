FROM python:3.13-bookworm as builder

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY pyproject.toml .
COPY src/ src/

RUN pip install --no-cache-dir .


FROM python:3.13-slim-bookworm as final

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv

COPY src/ src/
COPY alembic/ alembic/
COPY pyproject.toml .
COPY alembic.ini .

RUN mkdir -p /app/alembic/versions

ENV PATH="/opt/venv/bin:$PATH"

ENV PYTHONPATH="/app"

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]