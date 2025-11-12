# ▲ Vercel 前端部署步骤

## 快速部署

### 1. 安装 Vercel CLI
```bash
npm i -g vercel
```

### 2. 登录
```bash
vercel login
```

### 3. 部署
```bash
cd mgx_frontend
vercel --prod
```

### 4. 配置环境变量
在 Vercel 控制台：
1. 访问 https://vercel.com/dashboard
2. 选择项目
3. Settings → Environment Variables
4. 添加：
   - Key: `VITE_API_URL`
   - Value: `https://your-railway-backend.up.railway.app` (Railway 后端 URL)
   - Environment: Production, Preview, Development

### 5. 重新部署
在 Vercel 控制台点击 "Redeploy" 使环境变量生效

