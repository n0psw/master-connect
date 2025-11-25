FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt && \
    (pip list | grep -i passlib && (echo "ERROR: passlib should not be installed!" && exit 1) || echo "OK: passlib not installed") && \
    pip show bcrypt | grep Version

COPY apps/api/src/ ./src/
COPY apps/api/alembic.ini ./
COPY apps/api/alembic/ ./alembic/
COPY create_admin.py ./
COPY create_demo_users.py ./

RUN mkdir -p uploads/avatars uploads/payment_evidences

RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

EXPOSE 8000

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "src.main"]

