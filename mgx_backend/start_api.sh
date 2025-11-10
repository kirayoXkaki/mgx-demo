#!/bin/bash
# Start MGX Backend API Server

echo "🚀 Starting MGX Backend API..."

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Please create .env file with your OPENAI_API_KEY"
    echo "You can copy .env.example and fill in your API key"
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

# Start the API server
python api.py