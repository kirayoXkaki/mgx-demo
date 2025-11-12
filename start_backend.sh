#!/bin/bash
# Start MGX Backend API Server (independent)

echo "🚀 Starting MGX Backend API (independent mode)..."

cd "$(dirname "$0")/mgx_backend"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Please create .env file with your OPENAI_API_KEY"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY not set in .env file"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt
pip install -q fastapi uvicorn websockets python-multipart

echo "✅ Dependencies installed"
echo "🌐 Starting API server on http://localhost:8000"
echo "📖 API docs available at http://localhost:8000/docs"
echo ""

# Start the API server in background
# Use -u flag for unbuffered output to ensure logs are written immediately
WORKSPACE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$(dirname "$0")"
PYTHONPATH="$WORKSPACE_DIR:$PYTHONPATH" nohup python3 -u -m uvicorn mgx_backend.api:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &

echo "✅ Backend started in background (PID: $!)"
echo "📝 Logs: mgx_backend/api.log"
echo ""
echo "To stop: ./stop_backend.sh or kill $(lsof -ti:8000)"

