# Use Python 3.11 slim image để tránh greenlet build issues
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies required by Playwright
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libnss3 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm-dev \
    libsecret-1-0 \
    libu2f-udev \
    libvulkan1 \
    libxkbcommon0 \
    libxrandr2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxext6 \
    libxrender1 \
    libxi6 \
    libgl1-mesa-dri \
    libgobject-2.0-0 \
    libglib2.0-0 \
    libdbus-1-3 \
    libatk1.0-0 \
    libcups2 \
    libgio-2.0-0 \
    libdrm2 \
    libexpat1 \
    libxcb1 \
    libatspi2.0-0 \
    libx11-6 \
    libpango-1.0-0 \
    libcairo2 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

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
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright/

# Expose port (Render sẽ set PORT env var)
EXPOSE 10000

# Start command
CMD ["python", "web_server.py"]
