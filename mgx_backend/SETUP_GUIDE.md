# MGX Backend 配置指南

## 快速开始（3 步完成配置）

### 第 1 步：复制配置文件模板

```bash
cd /workspace/mgx_backend
cp .env.example .env
```

### 第 2 步：编辑 .env 文件，填入您的 API Key

使用任何文本编辑器打开 `.env` 文件：

```bash
# Linux/Mac
nano .env
# 或
vim .env

# Windows
notepad .env
```

修改这一行，将 `sk-your-api-key-here` 替换为您的实际 API key：

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
```

保存并关闭文件。

### 第 3 步：安装依赖并测试

```bash
# 安装依赖
pip install -r requirements.txt

# 测试配置是否正确
python examples/simple_test.py
```

---

## 详细配置说明

### .env 文件配置项

```bash
# 必填项
OPENAI_API_KEY=sk-your-api-key-here    # 您的 OpenAI API Key

# 可选项（有默认值）
OPENAI_MODEL=gpt-4-turbo               # 使用的模型
OPENAI_BASE_URL=https://api.openai.com/v1  # API 地址
MGX_WORKSPACE=./workspace              # 项目保存目录
```

### 获取 OpenAI API Key

1. 访问 https://platform.openai.com/api-keys
2. 登录您的 OpenAI 账号
3. 点击 "Create new secret key"
4. 复制生成的 key（以 `sk-` 开头）
5. 粘贴到 `.env` 文件中

### 配置优先级

系统会按以下优先级读取配置：

1. **代码中直接传入** - 最高优先级
   ```python
   generate_repo(idea="...", api_key="sk-xxx")
   ```

2. **环境变量** - 中等优先级
   ```bash
   export OPENAI_API_KEY="sk-xxx"
   ```

3. **.env 文件** - 最低优先级（但最方便）
   ```
   OPENAI_API_KEY=sk-xxx
   ```

---

## 使用示例

### 示例 1：使用 .env 文件（推荐）

```python
# 1. 确保 .env 文件已配置
# 2. 直接运行代码，会自动读取 .env

from mgx_backend.software_company import generate_repo

project_path = generate_repo("Create a calculator app")
print(f"Project: {project_path}")
```

### 示例 2：使用环境变量

```bash
export OPENAI_API_KEY="sk-your-key"
python mgx_backend/cli.py "Create a todo app"
```

### 示例 3：代码中直接传入

```python
from mgx_backend.software_company import generate_repo

project_path = generate_repo(
    idea="Create a game",
    api_key="sk-your-key"  # 直接传入
)
```

---

## 常见问题

### Q1: 找不到 .env 文件？

**A:** `.env` 文件需要您自己创建：

```bash
cd /workspace/mgx_backend
cp .env.example .env
# 然后编辑 .env 文件
```

### Q2: .env 文件不生效？

**A:** 确保：
1. 文件名是 `.env`（不是 `env.txt` 或其他）
2. 文件在正确的目录（`/workspace/mgx_backend/.env`）
3. 格式正确（`KEY=VALUE`，没有多余空格）
4. 重新运行程序

### Q3: API Key 无效？

**A:** 检查：
1. API Key 是否以 `sk-` 开头
2. 是否有多余的空格或引号
3. API Key 是否已过期或被撤销
4. OpenAI 账户是否有余额

### Q4: 如何验证配置是否正确？

**A:** 运行测试脚本：

```bash
cd /workspace
python mgx_backend/examples/simple_test.py
```

如果看到 "✅ LLM Response: ..." 说明配置成功。

---

## 安全提示

⚠️ **重要**：

1. **不要提交 .env 到 Git**
   - `.env` 已在 `.gitignore` 中
   - 只提交 `.env.example` 模板

2. **不要分享您的 API Key**
   - API Key 相当于密码
   - 如果泄露，立即在 OpenAI 后台撤销

3. **定期检查使用情况**
   - 访问 https://platform.openai.com/usage
   - 监控 API 调用和费用

4. **设置使用限制**
   - 在代码中设置预算：`investment=5.0`
   - 在 OpenAI 后台设置月度限额

---

## 完整使用流程

```bash
# 1. 进入项目目录
cd /workspace/mgx_backend

# 2. 创建并配置 .env
cp .env.example .env
nano .env  # 填入您的 API key

# 3. 安装依赖
pip install -r requirements.txt

# 4. 测试配置
python examples/simple_test.py

# 5. 生成第一个项目
python cli.py "Create a simple calculator" --investment 3.0

# 6. 查看生成的项目
ls -la workspace/
```

---

## 需要帮助？

如果遇到问题：

1. 查看 `README.md` - 完整文档
2. 查看 `USAGE.md` - 使用指南
3. 运行 `python test_mgx_backend.py` - 诊断问题
4. 检查 OpenAI API 状态：https://status.openai.com/

祝使用愉快！🚀