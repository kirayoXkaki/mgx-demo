#!/bin/bash
# 最简单的公网部署方案

echo "🌐 MGX 快速公网部署"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "📦 正在安装 ngrok..."
    if command -v brew &> /dev/null; then
        brew install ngrok/ngrok/ngrok
    else
        echo "❌ 请先安装 Homebrew 或手动安装 ngrok"
        echo "   下载: https://ngrok.com/download"
        exit 1
    fi
fi

echo "✅ ngrok 已就绪"
echo ""

# Check if ngrok is authenticated
if ! ngrok config check &> /dev/null; then
    echo "⚠️  ngrok 需要认证"
    echo ""
    echo "1. 访问 https://dashboard.ngrok.com/signup 注册账号"
    echo "2. 获取 authtoken"
    echo "3. 运行: ngrok config add-authtoken YOUR_TOKEN"
    echo ""
    read -p "按 Enter 继续（如果已配置）..."
fi

echo ""
echo "🚀 启动服务..."

# Ensure services are running
if ! curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    ./start_backend.sh
    sleep 3
fi

if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    ./start_frontend.sh
    sleep 3
fi

echo ""
echo "🌐 启动 ngrok 隧道..."
echo ""
echo "后端 (端口 8000) 将在新窗口启动..."
echo "前端 (端口 3000) 将在新窗口启动..."
echo ""

# Open ngrok web interface
open http://localhost:4040 2>/dev/null || echo "访问 http://localhost:4040 查看 ngrok 状态"

echo ""
echo "════════════════════════════════════════════════════"
echo "✅ 部署完成！"
echo "════════════════════════════════════════════════════"
echo ""
echo "📋 下一步："
echo ""
echo "1. 在新终端运行（暴露后端）："
echo "   ngrok http 8000"
echo ""
echo "2. 在另一个新终端运行（暴露前端）："
echo "   ngrok http 3000"
echo ""
echo "3. 从 ngrok 获取公网 URL（显示在终端或 http://localhost:4040）"
echo ""
echo "4. 更新前端配置："
echo "   编辑 mgx_frontend/.env.production"
echo "   设置 VITE_API_URL=后端-ngrok-url"
echo ""
echo "5. 重新构建前端："
echo "   cd mgx_frontend"
echo "   npm run build"
echo ""
echo "════════════════════════════════════════════════════"
