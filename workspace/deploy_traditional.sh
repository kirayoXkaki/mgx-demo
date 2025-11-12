#!/bin/bash

# Traditional deployment script (without Docker)
set -e

echo "🚀 Starting MGX Traditional Deployment..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration before continuing."
    echo "   Required: OPENAI_API_KEY, JWT_SECRET_KEY"
    exit 1
fi

# Load environment variables
source .env

# Check required variables
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
    echo "❌ ERROR: OPENAI_API_KEY is not set in .env file"
    echo "   Please edit .env and set your OpenAI API key"
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ] || [ "$JWT_SECRET_KEY" = "your-secret-key-change-in-production-min-32-chars" ]; then
    echo "⚠️  WARNING: JWT_SECRET_KEY is using default value"
    echo "   Generating a random secret key..."
    JWT_SECRET_KEY=$(openssl rand -hex 32)
    echo "JWT_SECRET_KEY=$JWT_SECRET_KEY" >> .env
    echo "✅ Generated new JWT_SECRET_KEY"
fi

echo "✅ Environment variables validated"

# Setup backend
echo ""
echo "🔧 Setting up backend..."
cd mgx_backend

if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing Python dependencies..."
source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Initialize database if needed
if [ ! -f "mgx_backend.db" ]; then
    echo "🗄️  Initializing database..."
    python init_db.py
fi

cd ..

# Setup frontend
echo ""
echo "🔧 Setting up frontend..."
cd mgx_frontend

if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Build frontend
echo "🏗️  Building frontend..."
VITE_API_URL=${VITE_API_URL:-http://localhost:8000} npm run build

cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 To start services:"
echo ""
echo "   Backend:"
echo "     cd mgx_backend"
echo "     source venv/bin/activate"
echo "     uvicorn api:app --host 0.0.0.0 --port 8000"
echo ""
echo "   Frontend (in another terminal):"
echo "     cd mgx_frontend"
echo "     npm run preview"
echo ""
echo "   Or use the existing scripts:"
echo "     ./start_backend.sh"
echo "     ./start_frontend.sh"
echo ""

