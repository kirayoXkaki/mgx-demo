# 🗄️ Supabase 数据库配置指南

## 📋 概述

所有任务数据现在保存在 Supabase PostgreSQL 数据库中，而不是内存中。这样可以：
- ✅ **数据持久化**：重启服务不会丢失数据
- ✅ **多实例支持**：多个服务实例共享同一数据库
- ✅ **可扩展性**：支持大量并发任务
- ✅ **数据安全**：自动备份和恢复

## 🚀 快速开始

### 1. 创建 Supabase 项目

1. 访问 https://supabase.com
2. 注册/登录账号
3. 点击 "New Project"
4. 填写项目信息：
   - **Name**: mgx-backend（或你喜欢的名字）
   - **Database Password**: 设置一个强密码（记住它！）
   - **Region**: 选择离你最近的区域
5. 等待项目创建完成（约 2 分钟）

### 2. 获取数据库连接字符串

1. 在 Supabase 控制台，进入项目
2. 点击 **Settings** → **Database**
3. 找到 **Connection string** 部分
4. 选择配置：
   - **Type**: `URI` ✅
   - **Source**: `Primary Database` ✅
   - **Method**: `Session Pooler` ⭐ **推荐**（解决 IPv4 兼容性问题）
     - 或者 `Direct connection`（如果 Railway 支持 IPv6）
5. 复制连接字符串，格式如下：
   ```
   # Session Pooler（推荐）
   postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:6543/postgres?pgbouncer=true
   
   # Direct connection（如果支持 IPv6）
   postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres
   ```
6. 将 `[YOUR-PASSWORD]` 替换为你的数据库密码

**⚠️ 重要提示**：
- 如果看到 "Not IPv4 compatible" 警告，**必须使用 Session Pooler**
- Session Pooler 使用端口 `6543`，Direct connection 使用端口 `5432`
- Railway 通常需要 IPv4，所以推荐使用 Session Pooler

### 3. 在 Railway 配置环境变量

1. 进入 Railway 项目控制台
2. 点击 **Variables** 标签页
3. 添加环境变量：
   - **Key**: `DATABASE_URL`
   - **Value**: 你的 Supabase 连接字符串
   - 示例：
     ```
     postgresql://postgres:your_password@db.abcdefghijklmnop.supabase.co:5432/postgres
     ```
4. 点击 **Save**

### 4. 重新部署

Railway 会自动检测环境变量变更并重新部署。或者手动触发：
- 在 Railway 控制台点击 **Deploy** → **Redeploy**

## 📊 数据库表结构

系统会自动创建以下表：

### tasks 表
存储所有生成任务的状态和结果：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| task_id | String(36) | UUID 任务ID（唯一索引） |
| status | String(20) | 状态：pending, running, completed, failed |
| progress | Integer | 进度：0-100 |
| current_stage | String(200) | 当前阶段描述 |
| cost | Float | 总成本 |
| idea | Text | 用户需求描述 |
| investment | Float | 投资金额 |
| n_round | Integer | 协作轮数 |
| result | JSON | 结果数据（项目路径、文件列表等） |
| error | Text | 错误信息（如果有） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### 其他表
- `users`: 用户信息
- `projects`: 项目信息
- `conversation_history`: 对话历史
- `cost_records`: 成本记录
- `sessions`: 用户会话

## 🔍 验证配置

### 检查数据库连接

部署后，检查 Railway 日志，应该看到：
```
✅ Database initialized: db.xxx.supabase.co:5432/postgres
```

### 测试任务创建

1. 通过 API 创建一个任务
2. 在 Supabase 控制台：
   - 进入 **Table Editor**
   - 选择 `tasks` 表
   - 应该能看到新创建的任务记录

## 🔒 安全建议

1. **使用环境变量**：不要将数据库密码硬编码在代码中
2. **启用 SSL**：Supabase 默认使用 SSL 连接
3. **限制访问**：在 Supabase 控制台设置 IP 白名单（如果需要）
4. **定期备份**：Supabase 提供自动备份，也可以手动导出

## 🛠️ 故障排查

### 连接失败

**错误**: `could not connect to server`

**解决方案**:
1. 检查 `DATABASE_URL` 环境变量是否正确
2. 确认密码中没有特殊字符需要 URL 编码
3. 检查 Supabase 项目是否正常运行

### 表不存在

**错误**: `relation "tasks" does not exist`

**解决方案**:
1. 系统会在首次启动时自动创建表
2. 如果表未创建，检查数据库连接是否正常
3. 查看 Railway 日志中的错误信息

### 连接池耗尽

**错误**: `too many connections`

**解决方案**:
1. Supabase 免费版有连接数限制
2. 检查是否有连接泄漏
3. 考虑升级到付费计划

## 📝 注意事项

1. **WebSocket 连接**：仍然保存在内存中（无法序列化到数据库）
2. **待发送消息**：`pending_messages` 仍然在内存中（临时数据）
3. **数据迁移**：如果之前使用内存存储，需要重新创建任务

## 🎉 完成！

配置完成后，所有任务数据都会持久化保存在 Supabase 数据库中，即使服务重启也不会丢失！

