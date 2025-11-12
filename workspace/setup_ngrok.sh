#!/bin/bash

# Quick ngrok setup script
set -e

echo "🌐 MGX ngrok 公网访问设置"
echo ""

# Check if services are running
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "⚠️  后端服务未运行，正在启动..."
    ./start_backend.sh
    sleep 3
fi

if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "⚠️  前端服务未运行，正在启动..."
    ./start_frontend.sh
    sleep 3
fi

echo "✅ 服务检查完成"
echo ""

# Check ngrok
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok 未安装"
    echo ""
    echo "安装方法："
    echo "  macOS: brew install ngrok/ngrok/ngrok"
    echo "  或访问: https://ngrok.com/download"
    echo ""
    echo "安装后需要："
    echo "  1. 注册账号: https://dashboard.ngrok.com/signup"
    echo "  2. 获取 authtoken"
    echo "  3. 运行: ngrok config add-authtoken YOUR_TOKEN"
    exit 1
fi

echo "✅ ngrok 已安装"
echo ""

# Start ngrok for backend
echo "🚀 启动后端 ngrok 隧道（端口 8000）..."
ngrok http 8000 --log=stdout > /tmp/ngrok_backend.log 2>&1 &
NGROK_BACKEND_PID=$!
echo "   后端 ngrok PID: $NGROK_BACKEND_PID"

sleep 5

# Get backend URL
BACKEND_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = [t for t in data.get('tunnels', []) if t.get('config', {}).get('addr', '').endswith(':8000')]
    if tunnels:
        print(tunnels[0]['public_url'])
    else:
        print('')
except:
    print('')
" 2>/dev/null)

if [ -z "$BACKEND_URL" ]; then
    echo "⚠️  无法获取后端 URL，请手动查看: http://localhost:4040"
    BACKEND_URL="https://your-backend-url.ngrok.io"
fi

echo "   后端公网地址: $BACKEND_URL"
echo ""

# Update frontend .env
echo "📝 更新前端配置..."
cd mgx_frontend

# Create .env.production if not exists
if [ ! -f .env.production ]; then
    echo "VITE_API_URL=$BACKEND_URL" > .env.production
else
    # Update existing
    if grep -q "VITE_API_URL" .env.production; then
        sed -i.bak "s|VITE_API_URL=.*|VITE_API_URL=$BACKEND_URL|" .env.production
    else
        echo "VITE_API_URL=$BACKEND_URL" >> .env.production
    fi
fi

echo "✅ 前端配置已更新: VITE_API_URL=$BACKEND_URL"
echo ""

# Rebuild frontend with new API URL
echo "🏗️  重新构建前端..."
VITE_API_URL=$BACKEND_URL npm run build > /dev/null 2>&1
echo "✅ 前端构建完成"
echo ""

cd ..

# Start ngrok for frontend (on different port to avoid conflict)
echo "🚀 启动前端 ngrok 隧道（端口 3000）..."
echo "   注意: 如果 4040 端口被占用，ngrok 会使用 4041"
ngrok http 3000 --log=stdout > /tmp/ngrok_frontend.log 2>&1 &
NGROK_FRONTEND_PID=$!
echo "   前端 ngrok PID: $NGROK_FRONTEND_PID"

sleep 5

# Get frontend URL
FRONTEND_URL=$(curl -s http://localhost:4041/api/tunnels 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    if tunnels:
        print(tunnels[0]['public_url'])
    else:
        print('')
except:
    print('')
" 2>/dev/null)

if [ -z "$FRONTEND_URL" ]; then
    # Try 4040 if 4041 doesn't work
    FRONTEND_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = [t for t in data.get('tunnels', []) if t.get('config', {}).get('addr', '').endswith(':3000')]
    if tunnels:
        print(tunnels[0]['public_url'])
    else:
        print('')
except:
    print('')
" 2>/dev/null)
fi

echo ""
echo "════════════════════════════════════════════════════"
echo "✅ 公网访问已配置完成！"
echo "════════════════════════════════════════════════════"
echo ""
echo "📋 访问地址："
echo "   前端公网: $FRONTEND_URL"
echo "   后端公网: $BACKEND_URL"
echo "   后端管理: http://localhost:4040"
echo ""
echo "🌐 分享给其他人："
echo "   让他们访问: $FRONTEND_URL"
echo ""
echo "⚠️  重要提示："
echo "   1. ngrok 免费版 URL 每次重启会变化"
echo "   2. 停止服务: kill $NGROK_BACKEND_PID $NGROK_FRONTEND_PID"
echo "   3. 查看日志: tail -f /tmp/ngrok_*.log"
echo ""
echo "════════════════════════════════════════════════════"

