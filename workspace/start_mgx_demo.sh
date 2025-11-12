#!/bin/bash
# Start both MGX Backend API and Frontend

echo "🚀 Starting MGX Demo Application..."
echo ""

# Check if .env exists in backend
if [ ! -f "mgx_backend/.env" ]; then
    echo "⚠️  Warning: mgx_backend/.env file not found"
    echo "Please create .env file with your OPENAI_API_KEY"
    echo ""
    echo "Quick setup:"
    echo "  cd mgx_backend"
    echo "  cp .env.example .env"
    echo "  # Edit .env and add your OpenAI API key"
    echo ""
    exit 1
fi

# Start backend in background
echo "📡 Starting Backend API..."
cd mgx_backend
chmod +x start_api.sh
./start_api.sh &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Start frontend
echo "🎨 Starting Frontend..."
cd mgx_frontend
chmod +x start_frontend.sh
./start_frontend.sh &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ MGX Demo is running!"
echo ""
echo "📡 Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait