# ✅ Vercel + Railway 部署检查清单

## 📋 部署前准备

- [ ] 代码已推送到 GitHub (`kirayoXkaki/mgx-demo`)
- [ ] 准备好 OpenAI API Key
- [ ] 注册 Railway 账号: https://railway.app
- [ ] 注册 Vercel 账号: https://vercel.com

---

## 🚂 Railway 后端部署

### 步骤 1: 创建项目
- [ ] 访问 https://railway.app
- [ ] 点击 "New Project"
- [ ] 选择 "Deploy from GitHub repo"
- [ ] 授权 GitHub 访问
- [ ] 选择仓库: `kirayoXkaki/mgx-demo`

### 步骤 2: 配置服务
- [ ] 进入项目设置 (Settings)
- [ ] 设置 **Root Directory**: `mgx_backend`
- [ ] 确认 **Build Command**: `pip install -r requirements.txt`
- [ ] 确认 **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`

### 步骤 3: 添加环境变量
在 **Variables** 标签页添加：

- [ ] `OPENAI_API_KEY` = `your-openai-api-key`
- [ ] `JWT_SECRET_KEY` = `fAkB2pKgvOS3KORwRRcdpk2aeLiCGKzWZwCpxKiHkyOVIZXxjoI2iUDVUaPhmXeo`
- [ ] `OPENAI_MODEL` = `gpt-4-turbo`
- [ ] `OPENAI_BASE_URL` = `https://api.openai.com/v1`

### 步骤 4: 获取后端 URL
- [ ] Railway 自动分配 URL
- [ ] 记下 URL: `https://your-app-production.up.railway.app`
- [ ] 测试健康检查: `curl https://your-app-production.up.railway.app/api/health`

---

## ▲ Vercel 前端部署

### 步骤 1: 安装 CLI
- [ ] 运行: `npm i -g vercel`
- [ ] 运行: `vercel login`

### 步骤 2: 部署
- [ ] 进入目录: `cd mgx_frontend`
- [ ] 运行: `vercel --prod`
- [ ] 选择项目设置（使用默认即可）

### 步骤 3: 配置环境变量
在 Vercel 控制台：

- [ ] 访问 https://vercel.com/dashboard
- [ ] 选择项目
- [ ] 进入 **Settings → Environment Variables**
- [ ] 添加变量:
  - Key: `VITE_API_URL`
  - Value: `https://your-railway-backend.up.railway.app` (Railway 后端 URL)
  - Environment: 选择 **Production, Preview, Development**

### 步骤 4: 重新部署
- [ ] 在 Vercel 控制台点击 **Deployments**
- [ ] 点击 **Redeploy** 使环境变量生效

---

## 🔧 更新后端 CORS（重要！）

部署前端后，需要更新后端 CORS 配置以允许 Vercel 域名：

1. 获取 Vercel 前端 URL（例如: `https://your-app.vercel.app`）

2. 更新 `mgx_backend/api.py` 中的 CORS 配置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-app.vercel.app",  # 添加 Vercel URL
        "https://your-custom-domain.com",  # 如果有自定义域名
        "http://localhost:3000",  # 保留本地开发
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)
```

3. 提交并推送更改：
```bash
git add mgx_backend/api.py
git commit -m "Update CORS for Vercel deployment"
git push origin main
```

4. Railway 会自动重新部署

---

## ✅ 验证部署

### 后端验证
- [ ] 访问: `https://your-railway-backend.up.railway.app/api/health`
- [ ] 应该返回: `{"status":"healthy","service":"MGX Backend API"}`
- [ ] 访问: `https://your-railway-backend.up.railway.app/docs`
- [ ] 应该看到 API 文档

### 前端验证
- [ ] 访问 Vercel 提供的 URL
- [ ] 测试登录功能
- [ ] 测试生成项目功能
- [ ] 检查浏览器控制台无错误

### 端到端测试
- [ ] 创建新用户
- [ ] 登录
- [ ] 输入提示词生成项目
- [ ] 验证文件系统显示正常
- [ ] 验证聊天消息显示正常

---

## 🎉 完成！

部署成功后：
- [ ] 分享 Vercel URL 给其他人
- [ ] 配置自定义域名（可选）
- [ ] 设置监控和告警（可选）

---

## 🆘 故障排查

### Railway 部署失败
- 检查 Deploy Logs
- 确认环境变量已设置
- 检查 Python 版本（需要 3.11+）

### Vercel 部署失败
- 检查 Build Logs
- 确认 `VITE_API_URL` 已设置
- 检查 Node.js 版本

### 前端无法连接后端
- 检查 `VITE_API_URL` 是否正确
- 检查后端 CORS 配置
- 查看浏览器控制台错误

---

**需要帮助？查看详细文档:**
- `DEPLOY_NOW.md` - 完整部署指南
- `RAILWAY_DEPLOY.md` - Railway 详细步骤
- `VERCEL_DEPLOY.md` - Vercel 详细步骤

