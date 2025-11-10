#!/bin/bash
# Start MGX Frontend Development Server

echo "🚀 Starting MGX Frontend..."

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "✅ Dependencies ready"
echo "🌐 Starting development server on http://localhost:3000"
echo ""

# Start the development server
npm run dev