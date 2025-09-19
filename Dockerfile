# Use Python 3.11 slim image để tránh greenlet build issues
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip và install build tools
RUN pip install --upgrade pip setuptools wheel

# Copy requirements first để cache dependencies
COPY requirements.txt .

# Install Python dependencies với greenlet binary wheel
RUN pip install --only-binary=:all: greenlet==3.0.1 && \
    pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright/

# Expose port (Render sẽ set PORT env var)
EXPOSE 10000

# Start command
CMD ["python", "web_server.py"]
