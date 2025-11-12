# 🚀 Vercel + Railway 快速部署指南

## 前置准备

✅ 确保代码已推送到 GitHub
✅ 准备好 OpenAI API Key
✅ 注册 Vercel 账号: https://vercel.com
✅ 注册 Railway 账号: https://railway.app

---

## 步骤一：部署后端到 Railway

### 1. 创建 Railway 项目

1. 访问 https://railway.app
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 授权 GitHub 访问
5. 选择您的仓库

### 2. 配置服务

在 Railway 项目设置中：

**Settings → Source:**
- Root Directory: `mgx_backend`

**Settings → Deploy:**
- Build Command: `pip install -r requirements.txt`
- Start Command: `cd mgx_backend && uvicorn api:app --host 0.0.0.0 --port $PORT`

### 3. 设置环境变量

在 Railway 的 **Variables** 标签页添加：

```
OPENAI_API_KEY=your-openai-api-key-here
JWT_SECRET_KEY=your-random-secret-key-min-32-chars
OPENAI_MODEL=gpt-4-turbo
OPENAI_BASE_URL=https://api.openai.com/v1
DATABASE_URL=postgresql://... (Railway 会自动提供 PostgreSQL)
```

**生成 JWT_SECRET_KEY:**
```bash
python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64)))"
```

### 4. 获取后端 URL

Railway 会自动分配一个 URL，例如：
- `https://your-app-production.up.railway.app`

**⚠️ 重要：记下这个 URL！**

### 5. 配置自定义域名（可选）

在 Railway 项目设置 → Settings → Domains 添加您的域名。

---

## 步骤二：部署前端到 Vercel

### 1. 安装 Vercel CLI

```bash
npm i -g vercel
```

### 2. 登录 Vercel

```bash
vercel login
```

### 3. 部署前端

```bash
cd mgx_frontend

# 设置后端 API URL（使用 Railway 的 URL）
export VITE_API_URL=https://your-app-production.up.railway.app

# 部署
vercel --prod
```

### 4. 在 Vercel 控制台设置环境变量

1. 访问 https://vercel.com/dashboard
2. 选择您的项目
3. 进入 **Settings → Environment Variables**
4. 添加：
   - **Key**: `VITE_API_URL`
   - **Value**: `https://your-app-production.up.railway.app` (Railway 后端 URL)
   - **Environment**: Production, Preview, Development (全选)

### 5. 重新部署使环境变量生效

在 Vercel 控制台点击 **Deployments → Redeploy**

---

## 步骤三：更新后端 CORS 配置

更新 `mgx_backend/api.py` 中的 CORS 配置，允许 Vercel 域名：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-vercel-app.vercel.app",
        "https://your-custom-domain.com",
        "http://localhost:3000",  # 保留本地开发
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)
```

提交并推送更改，Railway 会自动重新部署。

---

## 步骤四：验证部署

### 1. 检查后端

```bash
curl https://your-app-production.up.railway.app/api/health
```

应该返回: `{"status":"healthy","service":"MGX Backend API"}`

### 2. 检查前端

访问 Vercel 提供的 URL，测试：
- 登录功能
- 生成项目功能
- API 连接

### 3. 检查 API 文档

访问: `https://your-app-production.up.railway.app/docs`

---

## 自动化部署

Railway 和 Vercel 都支持自动部署：

- **Railway**: 推送代码到 GitHub 主分支自动部署
- **Vercel**: 推送代码到 GitHub 主分支自动部署

---

## 故障排查

### Railway 部署失败

1. 查看 Railway 的 Deploy Logs
2. 确认环境变量已设置
3. 检查 Python 版本（需要 3.11+）
4. 确认 `mgx_backend` 目录结构正确

### Vercel 部署失败

1. 查看 Vercel 的 Build Logs
2. 确认 `VITE_API_URL` 环境变量已设置
3. 检查 Node.js 版本
4. 确认构建命令正确

### 前端无法连接后端

1. 检查 `VITE_API_URL` 是否正确
2. 检查后端 CORS 配置
3. 查看浏览器控制台错误
4. 检查后端健康状态

---

## 成本

- **Vercel**: 完全免费（100GB 带宽/月）
- **Railway**: $5 免费额度/月（约 500 小时）

小规模使用完全免费！

---

## 下一步

部署完成后：
1. 配置自定义域名（可选）
2. 设置监控和告警
3. 配置备份策略
4. 优化性能

---

**🎉 部署完成后，您的应用就可以被全世界访问了！**

