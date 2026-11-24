FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr and writing pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    DB_PATH=/app/data/guestbook.db

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app/ /app/app/

# Create data directory for SQLite with non-root ownership
RUN mkdir -p /app/data && \
    useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8080

# Run uvicorn server binding to Cloud Run's $PORT
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}
