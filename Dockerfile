FROM python:3.9-slim

WORKDIR /app

# Install system dependencies required for aiomysql
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    python3-dev \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install honcho

# Copy application code
COPY . .

# Expose port (for documentation, Railway assigns its own)
EXPOSE 8000

# Start with Procfile using honcho (runs web and worker processes)
CMD ["honcho", "-f", "Procfile", "start"]
