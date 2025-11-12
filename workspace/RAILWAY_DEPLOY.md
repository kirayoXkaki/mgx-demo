# 🚂 Railway 后端部署步骤

## 快速部署

### 1. 访问 Railway
https://railway.app

### 2. 创建项目
- 点击 "New Project"
- 选择 "Deploy from GitHub repo"
- 授权 GitHub
- 选择仓库: `kirayoXkaki/mgx-demo`

### 3. 配置服务
在项目设置中：

**Settings → Source:**
- Root Directory: `mgx_backend`

**Settings → Deploy:**
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

### 4. 添加环境变量
在 **Variables** 标签页添加：

```
OPENAI_API_KEY=your-openai-api-key
JWT_SECRET_KEY=fAkB2pKgvOS3KORwRRcdpk2aeLiCGKzWZwCpxKiHkyOVIZXxjoI2iUDVUaPhmXeo
OPENAI_MODEL=gpt-4-turbo
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 5. 获取后端 URL
Railway 会自动分配 URL，例如：
`https://your-app-production.up.railway.app`

**⚠️ 记下这个 URL，部署前端时需要！**

