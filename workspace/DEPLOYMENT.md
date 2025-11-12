# MGX 项目部署指南

本指南将帮助您将 MGX 项目部署到生产环境。

## 部署方式

### 方式一：Docker Compose 部署（推荐）

这是最简单的部署方式，适合单服务器部署。

#### 前置要求

- Docker 和 Docker Compose
- 至少 2GB 可用内存
- 网络连接（用于访问 OpenAI API）

#### 部署步骤

1. **配置环境变量**

```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的配置
nano .env
```

必须配置的变量：
- `OPENAI_API_KEY`: 您的 OpenAI API 密钥
- `JWT_SECRET_KEY`: JWT 密钥（至少32个字符，用于生产环境）
- `VITE_API_URL`: 前端访问后端的 URL（生产环境应使用实际域名）

2. **运行部署脚本**

```bash
chmod +x deploy.sh
./deploy.sh
```

或者手动部署：

```bash
docker-compose build
docker-compose up -d
```

3. **验证部署**

- 前端: http://localhost
- 后端 API: http://localhost:8000
- API 文档: http://localhost:8000/docs

#### 管理服务

```bash
# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 更新代码后重新部署
docker-compose build
docker-compose up -d
```

---

### 方式二：云服务部署

#### 前端部署（Vercel/Netlify）

1. **准备构建**

```bash
cd mgx_frontend
npm install
VITE_API_URL=https://your-backend-domain.com npm run build
```

2. **部署到 Vercel**

```bash
# 安装 Vercel CLI
npm i -g vercel

# 部署
cd mgx_frontend
vercel
```

在 Vercel 控制台设置环境变量：
- `VITE_API_URL`: 您的后端 API URL

3. **部署到 Netlify**

```bash
# 安装 Netlify CLI
npm i -g netlify-cli

# 部署
cd mgx_frontend
netlify deploy --prod
```

#### 后端部署（Railway/Render）

1. **Railway 部署**

- 连接 GitHub 仓库
- 选择 `mgx_backend` 目录作为根目录
- 设置环境变量（见 `.env.example`）
- Railway 会自动检测 Python 并安装依赖

2. **Render 部署**

创建 `render.yaml`:

```yaml
services:
  - type: web
    name: mgx-backend
    env: python
    buildCommand: pip install -r mgx_backend/requirements.txt
    startCommand: uvicorn mgx_backend.api:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: JWT_SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        fromDatabase:
          name: mgx-db
          property: connectionString
```

---

### 方式三：传统服务器部署

#### 后端部署

1. **安装依赖**

```bash
cd mgx_backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **配置环境变量**

```bash
export OPENAI_API_KEY=your-key
export JWT_SECRET_KEY=your-secret
export DATABASE_URL=sqlite:///./mgx_backend.db
```

3. **使用 systemd 运行服务**

创建 `/etc/systemd/system/mgx-backend.service`:

```ini
[Unit]
Description=MGX Backend API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/mgx/metadev/workspace
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn mgx_backend.api:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl enable mgx-backend
sudo systemctl start mgx-backend
```

#### 前端部署

1. **构建前端**

```bash
cd mgx_frontend
npm install
VITE_API_URL=https://your-backend-domain.com npm run build
```

2. **使用 Nginx 部署**

创建 `/etc/nginx/sites-available/mgx`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    root /path/to/mgx/metadev/workspace/mgx_frontend/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/mgx /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 环境变量说明

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| `OPENAI_API_KEY` | OpenAI API 密钥 | ✅ | - |
| `OPENAI_MODEL` | 使用的模型 | ❌ | gpt-4-turbo |
| `OPENAI_BASE_URL` | API 基础 URL | ❌ | https://api.openai.com/v1 |
| `JWT_SECRET_KEY` | JWT 密钥 | ✅ | - |
| `DATABASE_URL` | 数据库连接字符串 | ❌ | sqlite:///./mgx_backend.db |
| `VITE_API_URL` | 前端 API URL | ❌ | http://localhost:8000 |
| `MGX_WORKSPACE` | 工作空间路径 | ❌ | ./workspace/workspace |

---

## 数据库配置

### SQLite（开发/小规模）

默认使用 SQLite，无需额外配置。

### PostgreSQL（生产环境）

1. **安装 PostgreSQL**

```bash
sudo apt-get install postgresql postgresql-contrib
```

2. **创建数据库**

```sql
CREATE DATABASE mgx_db;
CREATE USER mgx_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE mgx_db TO mgx_user;
```

3. **更新环境变量**

```bash
DATABASE_URL=postgresql://mgx_user:your_password@localhost:5432/mgx_db
```

4. **运行迁移**

```bash
cd mgx_backend
python init_db.py
```

---

## 安全建议

1. **更改默认密钥**: 确保 `JWT_SECRET_KEY` 是强随机字符串
2. **使用 HTTPS**: 生产环境必须使用 HTTPS
3. **限制 CORS**: 在生产环境中限制 `allow_origins`
4. **数据库安全**: 使用强密码，限制数据库访问
5. **API 密钥保护**: 不要将 API 密钥提交到代码仓库

---

## 故障排查

### 后端无法启动

```bash
# 查看日志
docker-compose logs backend

# 检查端口占用
netstat -tulpn | grep 8000
```

### 前端无法连接后端

1. 检查 `VITE_API_URL` 是否正确
2. 检查后端 CORS 配置
3. 检查网络连接和防火墙

### 数据库连接问题

```bash
# SQLite
ls -la mgx_backend/mgx_backend.db

# PostgreSQL
psql -U mgx_user -d mgx_db -c "SELECT 1;"
```

---

## 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建
docker-compose build

# 重启服务
docker-compose up -d
```

---

## 监控和维护

### 查看日志

```bash
# Docker
docker-compose logs -f

# Systemd
sudo journalctl -u mgx-backend -f
```

### 备份数据库

```bash
# SQLite
cp mgx_backend/mgx_backend.db backup_$(date +%Y%m%d).db

# PostgreSQL
pg_dump -U mgx_user mgx_db > backup_$(date +%Y%m%d).sql
```

---

## 支持

如有问题，请查看：
- 项目 README
- GitHub Issues
- 项目文档

