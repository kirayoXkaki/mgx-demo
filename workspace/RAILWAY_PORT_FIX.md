# 🔧 Railway PORT 环境变量修复

## ❌ 错误信息
```
Error: Invalid value for '--port': '$PORT' is not a valid integer.
```

## 🔍 问题原因

`$PORT` 环境变量没有被正确解析。在 Railway 中，启动命令需要正确处理环境变量。

---

## ✅ 解决方案

### 方案一：使用 sh -c（推荐）

在 Railway 的 **Custom Start Command** 中：

```bash
sh -c "uvicorn api:app --host 0.0.0.0 --port \$PORT"
```

或者使用默认值：

```bash
sh -c "uvicorn api:app --host 0.0.0.0 --port \${PORT:-8000}"
```

### 方案二：使用 Python 脚本

创建一个启动脚本 `start.sh`：

```bash
#!/bin/sh
exec uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}
```

然后在 Custom Start Command 中：
```bash
sh start.sh
```

### 方案三：使用 Dockerfile（最可靠）

Dockerfile 已经修复，使用：
```dockerfile
CMD sh -c "uvicorn api:app --host 0.0.0.0 --port ${PORT:-8000}"
```

---

## 🚀 快速修复步骤

### 如果使用 Custom Start Command：

1. 进入 Railway → Settings → Deploy
2. 找到 **Custom Start Command**
3. 修改为：
   ```
   sh -c "cd mgx_backend && uvicorn api:app --host 0.0.0.0 --port \$PORT"
   ```
   或者如果 Root Directory 已经是 `workspace/mgx_backend`：
   ```
   sh -c "uvicorn api:app --host 0.0.0.0 --port \$PORT"
   ```
4. 保存并重新部署

### 如果使用 Dockerfile：

Dockerfile 已经修复，确保：
1. Builder 选择 "Dockerfile"
2. Root Directory 设置为 `workspace/mgx_backend`
3. 重新部署

---

## 📋 完整配置检查

- [ ] Root Directory: `workspace/mgx_backend`
- [ ] Custom Start Command: `sh -c "uvicorn api:app --host 0.0.0.0 --port \$PORT"`
- [ ] 或者使用 Dockerfile（已修复）
- [ ] 环境变量 `PORT` 由 Railway 自动提供（无需手动设置）

---

## 🔍 验证

部署成功后，检查日志应该看到：
```
INFO:     Uvicorn running on http://0.0.0.0:XXXX (Press CTRL+C to quit)
```

而不是 `$PORT` 错误。

---

## 💡 为什么需要 sh -c？

在 Railway 的启动命令中，直接使用 `$PORT` 可能不会被 shell 正确展开。使用 `sh -c` 可以确保：
- 环境变量被正确解析
- 命令在正确的 shell 环境中执行
- 支持默认值语法 `${PORT:-8000}`

