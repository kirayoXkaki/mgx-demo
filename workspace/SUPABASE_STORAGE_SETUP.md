# 📦 Supabase Storage 配置指南

## 📋 概述

项目文件现在可以上传到 Supabase Storage，这样即使服务器重启，文件也不会丢失。系统会：

1. ✅ **自动上传**：项目生成完成后自动上传到 Supabase Storage
2. ✅ **优先下载**：下载时优先从 Supabase Storage 获取
3. ✅ **自动回退**：如果 Storage 中没有，回退到本地文件系统

## 🚀 快速开始

### ⚠️ 重要：使用同一个 Supabase 项目

**不需要创建新的项目或数据库！** 

Supabase 的一个 **Project（项目）** 包含多个服务：

- ✅ **Database（数据库）**：一个 PostgreSQL 数据库，存储结构化数据（users, projects, conversations 等表）
- ✅ **Storage（存储）**：文件存储服务，存储文件（项目 zip 文件）
- ✅ **Auth（认证）**：用户认证服务
- ✅ **Realtime（实时）**：实时数据同步服务

**所以：**
- ❌ **不是**两个数据库
- ✅ **是**一个 Project 包含多个服务（Database + Storage + 其他）

你只需要：
1. 使用**同一个 Supabase Project**（已经配置了 Database 的那个）
2. 添加 Storage 相关的环境变量（`SUPABASE_URL` 和 `SUPABASE_SERVICE_ROLE_KEY`）

### 1. 获取 Supabase 凭证

1. 访问你的 Supabase 项目：https://supabase.com（**使用已有的项目，不需要新建**）
2. 进入 **Settings** → **API**
3. 复制以下信息：
   - **Project URL** (`SUPABASE_URL`) - 应该和 `DATABASE_URL` 中的域名相同
   - **Service Role Key** (`SUPABASE_SERVICE_ROLE_KEY`) ⚠️ **重要：使用 Service Role Key，不是 anon key**

### 2. 在 Railway 配置环境变量

1. 进入 Railway 项目控制台
2. 点击 **Variables** 标签页
3. 添加以下环境变量（**在现有的 `DATABASE_URL` 基础上添加**）：

   ```
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
   ```

   **📝 说明**：
   - `SUPABASE_URL` 可以从 `DATABASE_URL` 中提取
     - 如果 `DATABASE_URL` 是：`postgresql://postgres:password@db.xxx.supabase.co:5432/postgres`
     - 那么 `SUPABASE_URL` 是：`https://xxx.supabase.co`（去掉 `db.` 前缀，使用 `https://`）
   - 必须使用 **Service Role Key**，不是 anon key
   - Service Role Key 有完整权限，可以创建 bucket 和上传文件
   - 不要将 Service Role Key 暴露给前端

### 3. 创建 Storage Bucket（可选）

系统会自动创建 `projects` bucket，但如果你想手动创建：

1. 在 Supabase 控制台，进入 **Storage**
2. 点击 **New bucket**
3. 设置：
   - **Name**: `projects`
   - **Public**: `false`（私有存储）
4. 点击 **Create bucket**

### 4. 重新部署

Railway 会自动检测环境变量变更并重新部署。

## 📊 工作原理

### 上传流程

1. 项目生成完成后
2. 系统创建 zip 文件（在内存中）
3. 上传到 Supabase Storage：`projects/{task_id}.zip`
4. 将 `storage_path` 保存到项目的 `extra_data` 中

### 下载流程

1. 尝试从 Supabase Storage 下载
2. 如果 Storage 中没有，回退到本地文件系统
3. 如果都找不到，返回 404 错误

## 🔍 验证配置

### 检查上传

部署后，生成一个新项目，查看 Railway 日志，应该看到：

```
📤 [API] Uploading project to Supabase Storage: {task_id}
✅ [Supabase] Project uploaded to Storage: projects/{task_id}.zip
✅ [Supabase] Storage path saved to project: projects/{task_id}.zip
```

### 检查 Storage

1. 在 Supabase 控制台，进入 **Storage** → **projects** bucket
2. 应该能看到上传的 zip 文件

### 测试下载

1. 点击 "Download Project" 按钮
2. 查看 Railway 日志，应该看到：

```
📥 [API] Attempting to download from Supabase Storage: projects/{task_id}.zip
✅ [API] Successfully downloaded from Supabase Storage: projects/{task_id}.zip
```

## 🛠️ 故障排查

### 上传失败

**错误**: `Failed to upload project to Supabase Storage`

**可能原因**:
1. `SUPABASE_URL` 或 `SUPABASE_SERVICE_ROLE_KEY` 未设置
2. Service Role Key 不正确
3. 网络连接问题

**解决方案**:
1. 检查环境变量是否正确设置
2. 确认使用的是 Service Role Key（不是 anon key）
3. 查看 Railway 日志中的详细错误信息

### 下载失败

**错误**: `Failed to download from Supabase Storage`

**可能原因**:
1. 文件未上传成功
2. Storage path 不正确
3. Bucket 不存在

**解决方案**:
1. 检查项目是否成功上传（查看 Supabase Storage）
2. 检查项目的 `extra_data.storage_path` 字段
3. 确认 `projects` bucket 存在

### Bucket 创建失败

**错误**: `Error checking/creating bucket`

**可能原因**:
1. Service Role Key 权限不足
2. Bucket 名称冲突

**解决方案**:
1. 确认使用 Service Role Key
2. 手动在 Supabase 控制台创建 bucket

## 📝 注意事项

1. **Service Role Key 安全**：
   - 只在后端使用，不要暴露给前端
   - 有完整权限，可以访问所有数据

2. **存储成本**：
   - Supabase 免费版有 1GB 存储空间
   - 超出后需要升级计划

3. **文件大小限制**：
   - 单个文件最大 50MB（Supabase 限制）
   - 如果项目很大，可能需要优化

4. **自动清理**：
   - 目前不会自动删除旧文件
   - 可以定期清理 Storage 中的旧项目

## 🎉 完成！

配置完成后，所有项目文件都会自动上传到 Supabase Storage，即使服务器重启也不会丢失！

