#!/bin/bash
# Stop MGX Backend API Server

echo "🛑 Stopping MGX Backend API..."

# Kill process on port 8000
PID=$(lsof -ti:8000)
if [ -n "$PID" ]; then
    echo "   Found process $PID on port 8000"
    kill -9 $PID 2>/dev/null
    echo "✅ Backend stopped"
else
    echo "   No process found on port 8000"
fi

