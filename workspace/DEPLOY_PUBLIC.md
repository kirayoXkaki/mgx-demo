# 🌐 MGX 公网部署指南

让其他人也能访问您的 MGX 应用。

## 方案一：使用 ngrok（最简单，适合测试）

### 1. 安装 ngrok

```bash
# macOS
brew install ngrok/ngrok/ngrok

# 或下载: https://ngrok.com/download
```

### 2. 注册并配置 ngrok

```bash
# 注册账号后获取 authtoken
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

### 3. 暴露服务

```bash
# 暴露前端（端口 3000）
ngrok http 3000

# 在另一个终端暴露后端（端口 8000）
ngrok http 8000
```

### 4. 配置前端 API URL

从 ngrok 获取后端公网 URL（例如：`https://abc123.ngrok.io`），然后：

```bash
# 更新 .env 文件
echo "VITE_API_URL=https://your-backend-ngrok-url.ngrok.io" >> mgx_frontend/.env.production

# 重新构建前端
cd mgx_frontend
npm run build
```

### 5. 使用脚本自动部署

```bash
chmod +x deploy_public.sh
./deploy_public.sh
```

---

## 方案二：云服务部署（推荐生产环境）

### 前端部署到 Vercel（免费）

1. **安装 Vercel CLI**

```bash
npm i -g vercel
```

2. **部署前端**

```bash
cd mgx_frontend

# 设置后端 API URL（先部署后端获取 URL）
export VITE_API_URL=https://your-backend.railway.app

# 部署
vercel --prod
```

3. **设置环境变量**

在 Vercel 控制台设置：
- `VITE_API_URL`: 您的后端 URL

### 后端部署到 Railway（免费额度）

1. **访问 Railway**
   - 访问 https://railway.app
   - 使用 GitHub 账号登录

2. **创建新项目**
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择您的仓库

3. **配置服务**
   - **Root Directory**: `mgx_backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`

4. **设置环境变量**
   - `OPENAI_API_KEY`: 您的 OpenAI API 密钥
   - `JWT_SECRET_KEY`: 随机字符串（至少32字符）
   - `DATABASE_URL`: Railway 会自动提供 PostgreSQL（可选）

5. **获取公网 URL**
   - Railway 会自动分配一个公网 URL
   - 例如：`https://your-app.railway.app`

6. **更新前端配置**
   - 在 Vercel 中设置 `VITE_API_URL` 为 Railway 后端 URL
   - 重新部署前端

---

## 方案三：部署到自己的服务器

### 使用 Nginx 反向代理

1. **配置 Nginx**

```nginx
# /etc/nginx/sites-available/mgx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /var/www/mgx-frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket
    location /api/ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

2. **配置 SSL（HTTPS）**

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取 SSL 证书
sudo certbot --nginx -d your-domain.com
```

---

## 方案四：使用 Cloudflare Tunnel（免费，稳定）

1. **安装 cloudflared**

```bash
# macOS
brew install cloudflare/cloudflare/cloudflared

# 或下载: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation
```

2. **创建隧道**

```bash
cloudflared tunnel create mgx
cloudflared tunnel route dns mgx your-domain.com
```

3. **配置隧道**

创建 `~/.cloudflared/config.yml`:

```yaml
tunnel: <tunnel-id>
credentials-file: /path/to/credentials.json

ingress:
  - hostname: your-domain.com
    service: http://localhost:3000
  - hostname: api.your-domain.com
    service: http://localhost:8000
  - service: http_status:404
```

4. **运行隧道**

```bash
cloudflared tunnel run mgx
```

---

## 快速对比

| 方案 | 难度 | 成本 | 稳定性 | 适用场景 |
|------|------|------|--------|----------|
| ngrok | ⭐ 简单 | 免费/付费 | ⭐⭐ | 测试、演示 |
| Vercel + Railway | ⭐⭐ 中等 | 免费额度 | ⭐⭐⭐⭐ | 生产环境 |
| 自建服务器 | ⭐⭐⭐ 复杂 | 服务器费用 | ⭐⭐⭐⭐⭐ | 企业级 |
| Cloudflare Tunnel | ⭐⭐ 中等 | 免费 | ⭐⭐⭐⭐ | 生产环境 |

---

## 推荐方案

**快速测试**: 使用 ngrok  
**生产环境**: Vercel (前端) + Railway (后端)  
**企业级**: 自建服务器 + Nginx + SSL

---

## 安全注意事项

1. **使用 HTTPS**: 生产环境必须使用 HTTPS
2. **限制 CORS**: 更新后端 CORS 配置，只允许您的域名
3. **API 密钥保护**: 不要在前端代码中暴露 API 密钥
4. **速率限制**: 考虑添加 API 速率限制
5. **身份验证**: 确保用户认证正常工作

---

## 故障排查

### ngrok 连接失败
- 检查防火墙设置
- 确认服务正在运行
- 检查 ngrok 账号状态

### 前端无法连接后端
- 检查 `VITE_API_URL` 是否正确
- 检查后端 CORS 配置
- 查看浏览器控制台错误

### Railway 部署失败
- 检查构建日志
- 确认环境变量已设置
- 检查 Python 版本兼容性

