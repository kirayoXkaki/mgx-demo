# ▲ Vercel 前端部署指南

## 后端 URL
```
https://mgx-demo-production.up.railway.app
```

## 部署步骤

### 1. 安装 Vercel CLI（如果还没有）

```bash
npm i -g vercel
```

### 2. 登录 Vercel

```bash
vercel login
```

会打开浏览器，使用 GitHub/Google/Email 登录。

### 3. 部署前端

```bash
cd workspace/mgx_frontend
vercel --prod
```

部署过程中会询问：
- **Set up and deploy?** → Yes
- **Which scope?** → 选择您的账号
- **Link to existing project?** → No（首次部署）
- **What's your project's name?** → mgx-frontend（或您喜欢的名字）
- **In which directory is your code located?** → `./`（当前目录）

### 4. 设置环境变量

部署完成后，在 Vercel 控制台：

1. 访问 https://vercel.com/dashboard
2. 选择您的项目（mgx-frontend）
3. 进入 **Settings → Environment Variables**
4. 添加环境变量：
   - **Key**: `VITE_API_URL`
   - **Value**: `https://mgx-demo-production.up.railway.app`
   - **Environment**: 选择 Production, Preview, Development（全选）

### 5. 重新部署使环境变量生效

在 Vercel 控制台：
1. 进入 **Deployments** 标签页
2. 点击最新的部署
3. 点击 **Redeploy** 按钮
4. 等待重新部署完成

### 6. 验证部署

访问 Vercel 提供的 URL（例如：`https://mgx-frontend.vercel.app`）

测试：
- 登录功能
- 生成项目功能
- API 连接

---

## 故障排查

### 部署失败

1. 检查构建日志
2. 确认 Node.js 版本兼容
3. 检查 `package.json` 中的构建脚本

### 前端无法连接后端

1. 检查 `VITE_API_URL` 环境变量是否正确设置
2. 确认后端 CORS 配置允许 Vercel 域名
3. 查看浏览器控制台错误

### 更新后端 CORS（如果需要）

如果前端无法连接后端，可能需要更新后端 CORS 配置：

在 `workspace/mgx_backend/api.py` 中：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-vercel-app.vercel.app",  # 添加 Vercel URL
        "https://mgx-demo-production.up.railway.app",  # 后端 URL
        "http://localhost:3000",  # 本地开发
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)
```

然后提交并推送，Railway 会自动重新部署。

---

## 完成！

部署完成后，您的应用就可以被全世界访问了！🌍

