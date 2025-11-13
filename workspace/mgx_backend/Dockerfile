FROM python:3.11-slim

WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code to mgx_backend directory
# This creates the structure: /app/mgx_backend/api.py, /app/mgx_backend/software_company.py
# So "from mgx_backend.software_company" will work
RUN mkdir -p /app/mgx_backend
COPY . /app/mgx_backend/

# Add /app to PYTHONPATH so Python can find mgx_backend module
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Start command - use mgx_backend.api since files are in /app/mgx_backend/
# Railway sets PORT environment variable, but provide fallback
# Also ensure we're listening on 0.0.0.0 (all interfaces)
CMD sh -c "PORT=\${PORT:-8000} && echo 'Starting on port: $PORT' && uvicorn mgx_backend.api:app --host 0.0.0.0 --port \$PORT"
