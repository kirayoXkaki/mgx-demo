# LLM 模型配置指南

## 当前配置

系统默认使用 `gpt-4-turbo` 模型。可以通过以下方式修改：

## 可用的 OpenAI 模型

### 推荐模型（按性能排序）

1. **gpt-4o** - 最新最强的模型（推荐）
   - 更好的代码生成能力
   - 更快的响应速度
   - 更好的上下文理解

2. **gpt-4-turbo** - 当前默认模型
   - 平衡的性能和成本
   - 良好的代码生成能力

3. **gpt-4** - 经典模型
   - 稳定可靠
   - 成本较高

4. **gpt-3.5-turbo** - 经济型
   - 速度快，成本低
   - 代码生成能力较弱

### 关于 GPT-5

⚠️ **重要提示**: GPT-5 目前（2024年11月）尚未正式发布。如果未来发布，模型名称可能是：
- `gpt-5`
- `gpt-5-turbo`
- 或其他 OpenAI 指定的名称

## 配置方法

### 方法 1: 修改 .env 文件（推荐）

编辑 `mgx_backend/.env` 文件：

```bash
# 使用 GPT-4o（推荐）
OPENAI_MODEL=gpt-4o

# 或使用 GPT-4 Turbo
OPENAI_MODEL=gpt-4-turbo

# 或使用 GPT-4
OPENAI_MODEL=gpt-4

# 或使用 GPT-3.5 Turbo（经济型）
OPENAI_MODEL=gpt-3.5-turbo

# 如果 GPT-5 发布后可用
OPENAI_MODEL=gpt-5
```

### 方法 2: 修改代码默认值

编辑 `mgx_backend/config.py`：

```python
class LLMConfig(BaseModel):
    model: str = "gpt-4o"  # 修改这里
```

或编辑 `mgx_backend/llm.py`：

```python
class OpenAILLM(BaseLLM):
    model: str = "gpt-4o"  # 修改这里
```

### 方法 3: 环境变量（临时）

```bash
export OPENAI_MODEL=gpt-4o
./start_backend.sh
```

## 模型对比

| 模型 | 代码质量 | 速度 | 成本 | 推荐场景 |
|------|---------|------|------|----------|
| gpt-4o | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | 生产环境，最佳质量 |
| gpt-4-turbo | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 平衡选择（当前默认） |
| gpt-4 | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | 稳定可靠 |
| gpt-3.5-turbo | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 快速测试，成本敏感 |

## 切换步骤

1. **修改配置**
   ```bash
   # 编辑 .env 文件
   cd mgx_backend
   nano .env  # 或使用其他编辑器
   # 修改 OPENAI_MODEL=gpt-4o
   ```

2. **重启后端**
   ```bash
   cd ..
   ./stop_backend.sh
   ./start_backend.sh
   ```

3. **验证配置**
   ```bash
   # 查看日志确认模型
   tail -f mgx_backend/api.log | grep -i model
   ```

## 注意事项

1. **API 密钥权限**: 确保你的 API 密钥有权限访问所选模型
2. **成本**: 不同模型的成本差异很大，注意预算
3. **速率限制**: 不同模型有不同的速率限制
4. **功能差异**: 某些模型可能不支持某些功能（如函数调用）

## 测试新模型

切换模型后，建议运行一个小型测试项目，确认：
- 模型可用性
- 代码生成质量
- 响应速度
- 成本消耗

