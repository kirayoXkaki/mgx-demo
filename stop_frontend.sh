#!/bin/bash
# Stop MGX Frontend Development Server

echo "🛑 Stopping MGX Frontend..."

# Kill process on port 3000
PID=$(lsof -ti:3000)
if [ -n "$PID" ]; then
    echo "   Found process $PID on port 3000"
    kill -9 $PID 2>/dev/null
    echo "✅ Frontend stopped"
else
    echo "   No process found on port 3000"
fi

