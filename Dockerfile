# ---- Base image ----
FROM python:3.11-slim

# Metadata
LABEL maintainer="openenv-hackathon"
LABEL description="Email Classification & Triage OpenEnv Environment"

# Environment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir httpx==0.27.0 && \
    pip install --no-cache-dir -r requirements.txt

# Copy source
COPY env/ ./env/
COPY server/ ./server/
COPY inference.py .

# Expose FastAPI port (Hugging Face Spaces default)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run the FastAPI server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "7860"]