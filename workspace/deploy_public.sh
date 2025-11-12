#!/bin/bash

# Public deployment script - Expose local services to internet
set -e

echo "🌐 MGX 公网部署脚本"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "📦 ngrok 未安装，正在检查安装方式..."
    echo ""
    echo "请选择安装方式："
    echo "1. 使用 Homebrew: brew install ngrok/ngrok/ngrok"
    echo "2. 下载: https://ngrok.com/download"
    echo ""
    echo "或者使用其他方案："
    echo "3. 部署到云服务（Vercel + Railway）"
    echo ""
    read -p "按 Enter 继续查看云服务部署方案..."
    exit 1
fi

echo "✅ ngrok 已安装"
echo ""

# Start backend if not running
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "🚀 启动后端服务..."
    ./start_backend.sh
    sleep 3
fi

# Start frontend if not running
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "🚀 启动前端服务..."
    ./start_frontend.sh
    sleep 3
fi

echo ""
echo "🌐 正在启动 ngrok 隧道..."
echo ""

# Start ngrok for frontend (port 3000)
echo "前端隧道 (端口 3000):"
ngrok http 3000 --log=stdout &
NGROK_FRONTEND_PID=$!

sleep 5

# Get ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | python3 -c "
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

if [ -z "$NGROK_URL" ]; then
    echo "❌ 无法获取 ngrok URL，请检查 ngrok 是否正常运行"
    echo "   访问 http://localhost:4040 查看 ngrok 状态"
    exit 1
fi

echo ""
echo "✅ 公网访问已配置！"
echo ""
echo "📋 访问信息："
echo "   前端公网地址: $NGROK_URL"
echo "   本地前端: http://localhost:3000"
echo "   本地后端: http://localhost:8000"
echo ""
echo "⚠️  注意："
echo "   1. ngrok 免费版每次重启 URL 会变化"
echo "   2. 需要更新前端 .env 中的 VITE_API_URL 为后端公网地址"
echo "   3. 后端也需要通过 ngrok 暴露（端口 8000）"
echo ""
echo "🛑 停止 ngrok: kill $NGROK_FRONTEND_PID"
echo ""

