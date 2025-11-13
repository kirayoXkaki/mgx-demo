FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code to mgx_backend directory
RUN mkdir -p /app/mgx_backend
COPY . /app/mgx_backend/

# Add /app to PYTHONPATH so Python can find mgx_backend module
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Start command - explicitly set host and port
# Use Python to ensure proper environment variable handling
CMD python -c "import os; port = int(os.environ.get('PORT', 8000)); print(f'Starting server on 0.0.0.0:{port}'); import subprocess; subprocess.run(['uvicorn', 'mgx_backend.api:app', '--host', '0.0.0.0', '--port', str(port)])"
