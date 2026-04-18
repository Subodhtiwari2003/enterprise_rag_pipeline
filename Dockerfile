# ── Single stage — simple and reliable on Render ──────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies into the system Python (no prefix tricks)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py ./
COPY api/ ./api/
COPY core/ ./core/
COPY data/ ./data/
COPY static/ ./static/

# ChromaDB persistence directory
RUN mkdir -p /app/chroma_db

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# main:app → main.py → FastAPI instance named 'app'
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]