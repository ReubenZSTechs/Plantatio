# Plantatio API.
# Torch and transformers are large; the agent needs them only when a model is
# actually configured, so they install from api/requirements.txt as pinned.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app:/app/api

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential curl \
 && rm -rf /var/lib/apt/lists/*

COPY api/requirements.txt ./api/requirements.txt
RUN pip install --no-cache-dir -r api/requirements.txt

# Only what the server imports at runtime.
COPY api/ ./api/
COPY backend/ ./backend/
COPY RAG/ ./RAG/
COPY training/configs/ ./training/configs/
COPY misc/ ./misc/

EXPOSE 8000

CMD ["uvicorn", "app.app:app", "--app-dir", "api", "--host", "0.0.0.0", "--port", "8000"]
