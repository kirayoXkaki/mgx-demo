# 服务管理指南

## 问题说明

如果你使用 `start_mgx_demo.sh` 启动服务，前后端进程会被关联在一起。当你按 `Ctrl+C` 或关闭终端时，两个进程会同时被终止。

## 解决方案：独立管理前后端

现在你可以使用独立的脚本来分别管理前后端服务：

### 启动服务

#### 方式 1：独立启动（推荐）

```bash
# 只启动后端
./start_backend.sh

# 只启动前端
./start_frontend.sh
```

#### 方式 2：同时启动（使用原脚本）

```bash
# 同时启动前后端（会关联在一起）
./start_mgx_demo.sh
```

### 停止服务

#### 方式 1：使用停止脚本

```bash
# 只停止后端
./stop_backend.sh

# 只停止前端
./stop_frontend.sh
```

#### 方式 2：使用端口号

```bash
# 停止后端（端口 8000）
lsof -ti:8000 | xargs kill -9

# 停止前端（端口 3000）
lsof -ti:3000 | xargs kill -9
```

### 查看服务状态

```bash
# 查看后端进程
lsof -ti:8000

# 查看前端进程
lsof -ti:3000

# 查看所有相关进程
ps aux | grep -E "(uvicorn|npm|node|vite)" | grep -v grep
```

### 查看日志

```bash
# 后端日志
tail -f mgx_backend/api.log

# 前端日志
tail -f frontend.log
```

## 推荐工作流程

1. **开发时**：使用独立启动脚本，可以单独重启后端或前端
   ```bash
   ./start_backend.sh   # 启动后端
   ./start_frontend.sh  # 启动前端
   ```

2. **需要重启后端时**：
   ```bash
   ./stop_backend.sh
   ./start_backend.sh
   ```

3. **需要重启前端时**：
   ```bash
   ./stop_frontend.sh
   ./start_frontend.sh
   ```

4. **完全停止时**：
   ```bash
   ./stop_backend.sh
   ./stop_frontend.sh
   ```

## 注意事项

- 使用 `start_backend.sh` 和 `start_frontend.sh` 启动的服务会在后台运行，即使关闭终端也不会停止
- 使用 `start_mgx_demo.sh` 启动的服务会在前台运行，关闭终端或按 `Ctrl+C` 会同时停止前后端
- 所有脚本都使用 `nohup` 在后台运行，日志会保存到文件中

