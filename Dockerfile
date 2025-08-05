# Multi-stage build for optimized Hugging Face deployment
FROM python:3.10-slim as builder

# Set build arguments
ARG DEBIAN_FRONTEND=noninteractive

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.10-slim

# Set environment variables for production
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=-1
ENV TF_CPP_MIN_LOG_LEVEL=2
ENV PORT=7860

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app

# Set working directory
WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Download NLTK data as app user
USER app
RUN python -c "import nltk; nltk.download('punkt', download_dir='/home/app/nltk_data'); nltk.download('stopwords', download_dir='/home/app/nltk_data')"
ENV NLTK_DATA=/home/app/nltk_data

# Switch back to root to copy files and set permissions
USER root

# Copy application files
COPY --chown=app:app main.py .
COPY --chown=app:app emotion_model.h5 .
COPY --chown=app:app tokenizer.pkl .
COPY --chown=app:app static/ ./static/

# Create cache directory for Hugging Face transformers
RUN mkdir -p /home/app/.cache && chown -R app:app /home/app/.cache
ENV HF_HOME=/home/app/.cache/huggingface

# Switch to app user
USER app

# Expose port (Hugging Face Spaces uses 7860)
EXPOSE $PORT

# Health check optimized for production
HEALTHCHECK --interval=60s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# Run the application with optimized settings for Hugging Face
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT --workers 1 --timeout-keep-alive 30"]
