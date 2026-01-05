# Python Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies with error handling
RUN pip install --no-cache-dir -r requirements.txt || pip install --no-cache-dir -r requirements.txt --default-timeout=100

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/ai-models /app/uploads/ai_analysis /app/uploads/ai_training /app/uploads/backups

# Make startup script executable
RUN chmod +x /app/start.sh

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3001/api/health || exit 1

# Run startup script
CMD ["/app/start.sh"]
