# MGX Demo Deployment Guide

Complete guide for deploying the MGX Demo application to production.

## 📋 Table of Contents

1. [Local Development](#local-development)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Monitoring](#monitoring)

---

## 🏠 Local Development

### Quick Start

```bash
# 1. Configure backend
cd /workspace/mgx_backend
cp .env.example .env
# Edit .env: Add your OPENAI_API_KEY

# 2. Start everything
cd /workspace
./start_mgx_demo.sh

# Access at:
# - Frontend: http://localhost:3000
# - Backend: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

---

## 🚀 Production Deployment

### Backend Deployment (FastAPI)

#### Option 1: Using Uvicorn + Gunicorn

```bash
# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn mgx_backend.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300
```

#### Option 2: Using systemd

Create `/etc/systemd/system/mgx-backend.service`:

```ini
[Unit]
Description=MGX Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/mgx_backend
Environment="PATH=/var/www/mgx_backend/venv/bin"
EnvironmentFile=/var/www/mgx_backend/.env
ExecStart=/var/www/mgx_backend/venv/bin/gunicorn \
  mgx_backend.api:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable mgx-backend
sudo systemctl start mgx-backend
sudo systemctl status mgx-backend
```

### Frontend Deployment (React)

#### Build for Production

```bash
cd mgx_frontend

# Set production API URL
echo "VITE_API_URL=https://api.yourdomain.com" > .env.production

# Build
npm run build

# Output will be in dist/
```

#### Deploy to Nginx

```nginx
# /etc/nginx/sites-available/mgx-frontend
server {
    listen 80;
    server_name yourdomain.com;
    root /var/www/mgx_frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api/ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/mgx-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🐳 Docker Deployment

### Backend Dockerfile

Create `mgx_backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir fastapi uvicorn gunicorn websockets

# Copy application
COPY . .

# Expose port
EXPOSE 8000

# Run application
CMD ["gunicorn", "api:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "300"]
```

### Frontend Dockerfile

Create `mgx_frontend/Dockerfile`:

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./mgx_backend
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL=gpt-4-turbo
    volumes:
      - ./workspace:/app/workspace
    restart: unless-stopped

  frontend:
    build: ./mgx_frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    restart: unless-stopped
```

Deploy:
```bash
# Set environment variables
export OPENAI_API_KEY=your-key-here

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## ☁️ Cloud Deployment

### Deploy to Railway

1. **Backend**:
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize project
cd mgx_backend
railway init

# Add environment variables
railway variables set OPENAI_API_KEY=your-key

# Deploy
railway up
```

2. **Frontend**:
```bash
cd mgx_frontend

# Set backend URL
railway variables set VITE_API_URL=https://your-backend.railway.app

# Deploy
railway up
```

### Deploy to Render

1. **Backend** (Web Service):
   - Build Command: `pip install -r requirements.txt && pip install fastapi uvicorn gunicorn`
   - Start Command: `gunicorn api:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
   - Environment Variables: Add `OPENAI_API_KEY`

2. **Frontend** (Static Site):
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
   - Environment Variables: Add `VITE_API_URL`

### Deploy to Vercel (Frontend) + Railway (Backend)

**Backend on Railway**:
```bash
cd mgx_backend
railway init
railway up
# Note the URL: https://your-app.railway.app
```

**Frontend on Vercel**:
```bash
cd mgx_frontend

# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod

# Set environment variable
vercel env add VITE_API_URL production
# Enter: https://your-app.railway.app
```

---

## 📊 Monitoring

### Health Check Endpoint

Add to `api.py`:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "tasks": len(tasks)
    }
```

### Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mgx_backend.log'),
        logging.StreamHandler()
    ]
)
```

### Monitoring with Prometheus

```python
from prometheus_client import Counter, Histogram, generate_latest

request_count = Counter('mgx_requests_total', 'Total requests')
request_duration = Histogram('mgx_request_duration_seconds', 'Request duration')

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## 🔒 Security

### Environment Variables

Never commit `.env` files. Use:
- Railway/Render: Built-in environment variables
- Docker: `docker-compose.yml` with `.env` file
- Systemd: `EnvironmentFile` directive

### CORS Configuration

```python
# Production CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/generate")
@limiter.limit("5/minute")
async def generate(request: Request, ...):
    ...
```

---

## 🧪 Testing

### Backend Tests

```bash
cd mgx_backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd mgx_frontend
npm run test
```

### Load Testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test backend
ab -n 100 -c 10 http://localhost:8000/health
```

---

## 📈 Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml
services:
  backend:
    deploy:
      replicas: 4
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    depends_on:
      - backend
```

### Load Balancer (Nginx)

```nginx
upstream backend {
    least_conn;
    server backend1:8000;
    server backend2:8000;
    server backend3:8000;
    server backend4:8000;
}

server {
    location /api {
        proxy_pass http://backend;
    }
}
```

---

## 🔄 CI/CD

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy MGX Demo

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Railway
        run: |
          npm install -g @railway/cli
          railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Vercel
        run: |
          npm install -g vercel
          vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

## 📞 Support

For deployment issues:
- Check logs: `docker-compose logs -f`
- Verify environment variables
- Test health endpoint: `curl http://localhost:8000/health`
- Check API docs: `http://localhost:8000/docs`

---

**Happy Deploying! 🚀**