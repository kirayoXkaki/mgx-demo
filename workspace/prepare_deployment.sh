#!/bin/bash

# Prepare code for Vercel + Railway deployment
set -e

echo "🔧 准备 Vercel + Railway 部署..."
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 初始化 Git 仓库..."
    git init
    echo "✅ Git 仓库已初始化"
fi

# Check if .gitignore exists
if [ ! -f ".gitignore" ]; then
    echo "📝 创建 .gitignore..."
    cat > .gitignore << 'EOF'
# Environment
.env
.env.local
.env.production

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv

# Node
node_modules/
dist/
build/
*.log

# Database
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary
tmp/
temp/
EOF
    echo "✅ .gitignore 已创建"
fi

# Generate JWT secret if needed
if grep -q "your-secret-key-change-in-production" .env 2>/dev/null; then
    echo "🔑 生成 JWT_SECRET_KEY..."
    JWT_SECRET=$(python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64)))")
    sed -i.bak "s|JWT_SECRET_KEY=.*|JWT_SECRET_KEY=$JWT_SECRET|" .env
    echo "✅ JWT_SECRET_KEY 已生成"
fi

# Check if code is committed
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ 代码已提交"
else
    echo "📝 检测到未提交的更改..."
    echo ""
    echo "建议提交代码："
    echo "  git add ."
    echo "  git commit -m 'Prepare for deployment'"
    echo "  git push origin main"
fi

echo ""
echo "✅ 部署准备完成！"
echo ""
echo "📋 下一步："
echo ""
echo "1. 确保代码已推送到 GitHub"
echo "2. 访问 https://railway.app 部署后端"
echo "3. 访问 https://vercel.com 部署前端"
echo ""
echo "详细步骤请查看: DEPLOY_NOW.md"
echo ""

