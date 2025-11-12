#!/bin/bash
# 交互式环境变量配置脚本

echo "🔧 MGX 环境变量配置"
echo ""

# Generate JWT secret
JWT_SECRET=$(python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64)))")

echo "请输入您的 OpenAI API Key:"
read -s OPENAI_KEY

if [ -z "$OPENAI_KEY" ]; then
    echo "⚠️  未输入 API Key，将使用占位符"
    OPENAI_KEY="your-openai-api-key-here"
fi

# Update .env file
cat > .env << ENVFILE
# OpenAI Configuration
OPENAI_API_KEY=$OPENAI_KEY
OPENAI_MODEL=gpt-4-turbo
OPENAI_BASE_URL=https://api.openai.com/v1

# Database Configuration
DATABASE_URL=sqlite:///./mgx_backend/mgx_backend.db

# JWT Configuration
JWT_SECRET_KEY=$JWT_SECRET
JWT_ALGORITHM=HS256

# Frontend API URL
VITE_API_URL=http://localhost:8000

# Workspace Configuration
MGX_WORKSPACE=./workspace/workspace
ENVFILE

echo ""
echo "✅ 环境变量已配置完成！"
echo "   JWT_SECRET_KEY 已自动生成"
if [ "$OPENAI_KEY" != "your-openai-api-key-here" ]; then
    echo "   OPENAI_API_KEY 已设置"
else
    echo "   ⚠️  OPENAI_API_KEY 需要手动设置"
fi
