# ── Stage 1: Build dependencies ──────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# Install only what's needed to compile packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install pinned versions ignoring dependency conflicts, then reinstall uvicorn with deps
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --no-deps --prefix=/install -r requirements.txt && \
    pip install --no-cache-dir --prefix=/install "uvicorn==0.34.0"


# ── Stage 2: Runtime image ────────────────────────────────────────────────────
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy installed packages from builder stage
COPY --from=builder /install /usr/local

# Copy application code (your structure: main.py, api/, core/)
COPY main.py ./main.py
COPY api/ ./api/
COPY core/ ./core/

# Create directory for ChromaDB persistence
RUN mkdir -p /app/chroma_db

# Non-root user for security
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check (make sure you add a /health route in main.py)
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Start FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
