# 🚀 云服务部署指南（Vercel + Railway）

让您的应用永久在线，任何人都可以访问。

## 前置准备

1. GitHub 账号
2. Vercel 账号（免费）：https://vercel.com
3. Railway 账号（免费额度）：https://railway.app
4. OpenAI API Key

---

## 步骤一：部署后端到 Railway

### 1. 准备代码

确保代码已推送到 GitHub：

```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2. 在 Railway 创建项目

1. 访问 https://railway.app
2. 点击 "New Project"
3. 选择 "Deploy from GitHub repo"
4. 选择您的仓库

### 3. 配置服务

在 Railway 项目设置中：

- **Root Directory**: `mgx_backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`

### 4. 设置环境变量

在 Railway 的 Variables 标签页添加：

```
OPENAI_API_KEY=your-openai-api-key
JWT_SECRET_KEY=your-random-secret-key-min-32-chars
DATABASE_URL=postgresql://... (Railway 会自动提供)
```

### 5. 获取后端 URL

Railway 会自动分配一个 URL，例如：
- `https://your-app.railway.app`

**记下这个 URL，下一步需要用到！**

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
export VITE_API_URL=https://your-app.railway.app

# 部署
vercel --prod
```

### 4. 在 Vercel 控制台设置环境变量

1. 访问 https://vercel.com/dashboard
2. 选择您的项目
3. 进入 Settings > Environment Variables
4. 添加：
   - `VITE_API_URL`: `https://your-app.railway.app`

### 5. 重新部署

在 Vercel 控制台点击 "Redeploy" 使环境变量生效。

---

## 步骤三：更新后端 CORS 配置

更新 `mgx_backend/api.py` 中的 CORS 配置：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-vercel-app.vercel.app",
        "https://your-custom-domain.com",
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

## 步骤四：配置自定义域名（可选）

### Vercel 自定义域名

1. 在 Vercel 项目设置中添加域名
2. 按照提示配置 DNS

### Railway 自定义域名

1. 在 Railway 项目设置中添加自定义域名
2. 配置 DNS 记录

---

## 验证部署

1. **检查后端健康**
   ```bash
   curl https://your-app.railway.app/api/health
   ```

2. **访问前端**
   - 打开 Vercel 提供的 URL
   - 测试登录和功能

3. **检查 API 文档**
   - 访问: `https://your-app.railway.app/docs`

---

## 持续部署

Railway 和 Vercel 都支持自动部署：

- **Railway**: 推送代码到 GitHub 主分支自动部署
- **Vercel**: 推送代码到 GitHub 主分支自动部署

---

## 成本估算

### 免费额度

- **Vercel**: 
  - 100GB 带宽/月
  - 无限请求
  - 完全免费

- **Railway**: 
  - $5 免费额度/月
  - 约 500 小时运行时间
  - 超出后按使用付费

### 预计成本

- **小规模使用**: $0/月（完全免费）
- **中等使用**: $5-10/月
- **大规模使用**: $20+/月

---

## 故障排查

### Railway 部署失败

1. 检查构建日志
2. 确认环境变量已设置
3. 检查 Python 版本（需要 3.11+）

### Vercel 部署失败

1. 检查构建日志
2. 确认 `VITE_API_URL` 已设置
3. 检查 Node.js 版本

### 前端无法连接后端

1. 检查 `VITE_API_URL` 是否正确
2. 检查后端 CORS 配置
3. 查看浏览器控制台错误

---

## 安全建议

1. ✅ 使用 HTTPS（Vercel 和 Railway 自动提供）
2. ✅ 限制 CORS 来源
3. ✅ 使用强 JWT 密钥
4. ✅ 定期更新依赖
5. ✅ 监控 API 使用量

---

**部署完成后，您的应用就可以被全世界访问了！** 🌍

