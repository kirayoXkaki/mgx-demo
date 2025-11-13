FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start command
# 关键：PYTHONPATH 指向 /app，这样 Python 可以在 /app 下找到 mgx_backend 模块
CMD sh -c "PYTHONPATH=/app uvicorn api:app --host 0.0.0.0 --port \${PORT:-8000}"
