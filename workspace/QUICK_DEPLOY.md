# 🚀 MGX 快速部署指南

## 方式一：Docker Compose 一键部署（最简单）

### 1. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（必须设置）
nano .env
```

**必须配置的变量：**
- `OPENAI_API_KEY`: 您的 OpenAI API 密钥
- `JWT_SECRET_KEY`: 至少32个字符的随机字符串（用于生产环境）

### 2. 运行部署脚本

```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. 访问应用

- **前端**: http://localhost
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

---

## 方式二：云服务部署（推荐生产环境）

### 前端部署到 Vercel（免费）

```bash
cd mgx_frontend

# 安装 Vercel CLI
npm i -g vercel

# 部署
vercel

# 设置环境变量
vercel env add VITE_API_URL production
# 输入您的后端 URL，例如: https://your-backend.railway.app
```

### 后端部署到 Railway（免费额度）

1. 访问 https://railway.app
2. 连接 GitHub 仓库
3. 选择 `mgx_backend` 目录
4. 设置环境变量：
   - `OPENAI_API_KEY`
   - `JWT_SECRET_KEY`
   - `DATABASE_URL` (可选，默认使用 SQLite)
5. Railway 会自动部署

### 后端部署到 Render（免费）

1. 访问 https://render.com
2. 创建新的 Web Service
3. 连接 GitHub 仓库
4. 设置：
   - **Build Command**: `pip install -r mgx_backend/requirements.txt`
   - **Start Command**: `cd mgx_backend && uvicorn api:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables**: 添加 `OPENAI_API_KEY` 和 `JWT_SECRET_KEY`

---

## 方式三：传统服务器部署

### 后端部署

```bash
# 1. 安装依赖
cd mgx_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 设置环境变量
export OPENAI_API_KEY=your-key
export JWT_SECRET_KEY=your-secret-key

# 3. 运行服务
uvicorn api:app --host 0.0.0.0 --port 8000
```

### 前端部署

```bash
# 1. 构建
cd mgx_frontend
VITE_API_URL=https://your-backend-domain.com npm run build

# 2. 部署到 Nginx
sudo cp -r dist/* /var/www/html/
```

---

## 环境变量说明

| 变量 | 说明 | 必需 |
|------|------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | ✅ |
| `JWT_SECRET_KEY` | JWT 密钥（至少32字符） | ✅ |
| `OPENAI_MODEL` | 使用的模型 | ❌ |
| `VITE_API_URL` | 前端 API URL | ❌ |

---

## 验证部署

```bash
# 检查后端健康状态
curl http://localhost:8000/api/health

# 应该返回: {"status":"healthy","service":"MGX Backend API"}
```

---

## 常见问题

### 1. 端口被占用

```bash
# 检查端口
lsof -i :8000
lsof -i :80

# 修改 docker-compose.yml 中的端口映射
```

### 2. 前端无法连接后端

- 检查 `VITE_API_URL` 是否正确
- 检查后端 CORS 配置
- 检查防火墙设置

### 3. 数据库问题

```bash
# SQLite 数据库位置
ls -la mgx_backend/mgx_backend.db

# 如果需要重置数据库
rm mgx_backend/mgx_backend.db
python mgx_backend/init_db.py
```

---

## 更新部署

```bash
# Docker 方式
git pull
docker-compose build
docker-compose up -d

# 传统方式
git pull
# 重启服务
```

---

详细部署文档请查看 `DEPLOYMENT.md`

