# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Add the src directory to Python path
ENV PYTHONPATH=/app/src:$PYTHONPATH

# Create mount point for local volume
VOLUME /app

# Environment variables for API
ENV API_PORT=8001
ENV API_HOST=0.0.0.0

# Environment variables for services
ENV MARKET_ANALYSIS_HOST=market-analysis
ENV MARKET_ANALYSIS_PORT=8000
ENV TRADE_DISCOVERY_HOST=trade-discovery
ENV TRADE_DISCOVERY_PORT=8002

# Expose API port
EXPOSE 8001

# Set the default command to run the API server
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
