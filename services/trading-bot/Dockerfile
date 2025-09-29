# ======================================================================================
# Multi-stage build for the IQ Option Trading Bot API
# ======================================================================================

FROM python:3.11-slim AS base

# Set environment variables for Python
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# Create working directory
WORKDIR /app

# Install system dependencies and security updates
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    wget \
    # Required for IQ Option API
    build-essential \
    libssl-dev \
    libffi-dev \
    # Cleanup
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ======================================================================================
# Dependencies stage - Install Python packages
# ======================================================================================
FROM base AS dependencies

# Copy requirements and install Python dependencies
COPY requirements.txt .

# Install Python dependencies with caching
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ======================================================================================
# Runtime stage - Final application image
# ======================================================================================
FROM base AS runtime

# Copy installed Python dependencies from the dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Create application user for security
RUN useradd --create-home --shell /bin/bash --uid 1000 app

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/custom_indicators /app/triggers /app/news && \
    chown -R app:app /app

# Copy project files
COPY --chown=app:app . .

# Create example manifest files if they don't exist
RUN if [ ! -f custom_indicators/CustomIndicator.yml ]; then \
        mkdir -p custom_indicators triggers news && \
        echo "name: ExampleIndicator\nversion: 1.0.0\ndescription: Example custom indicator\ntype: indicator" > custom_indicators/CustomIndicator.yml && \
        echo "name: ExampleTrigger\nversion: 1.0.0\ndescription: Example trigger\ntype: trigger" > triggers/CustomTrigger.yml && \
        echo "name: ExampleNewsFeed\nversion: 1.0.0\ndescription: Example news feed\ntype: news_feed" > news/NewsSentimentFeed.yml; \
    fi

# Ensure proper permissions
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]