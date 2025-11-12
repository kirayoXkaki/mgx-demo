#!/bin/bash
# Start MGX Frontend Development Server (independent)

echo "🚀 Starting MGX Frontend (independent mode)..."

cd "$(dirname "$0")/mgx_frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "✅ Dependencies ready"
echo "🌐 Starting development server on http://localhost:3000"
echo ""

# Start the development server in background
nohup npm run dev > ../frontend.log 2>&1 &

echo "✅ Frontend started in background (PID: $!)"
echo "📝 Logs: frontend.log"
echo ""
echo "To stop: ./stop_frontend.sh or kill $(lsof -ti:3000)"

