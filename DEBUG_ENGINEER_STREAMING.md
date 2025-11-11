# Engineer 流文件推送问题调试指南

## 问题描述
Engineer 的代码文件没有通过 WebSocket 推送到前端。

## 可能的原因

### 1. FILE: 标记没有被检测到
- **检查点**: 查看日志中是否有 `🔍 [Stream] WriteCode total FILE: markers` 输出
- **原因**: LLM 可能没有按照 `FILE:` 格式输出代码
- **解决**: 检查 `write_code.py` 中的 prompt，确保明确要求使用 `FILE:` 格式

### 2. 内容提取正则表达式失败
- **检查点**: 查看日志中是否有 `📤 [Stream] Sent first file_content` 输出
- **原因**: 正则表达式可能无法匹配 LLM 的实际输出格式
- **解决**: 检查 `accumulated_content` 的实际格式，调整正则表达式

### 3. progress_callback 没有正确传递
- **检查点**: 查看日志中 `progress_callback available: True/False`
- **原因**: `progress_callback` 可能没有正确设置到 `context.kwargs`
- **解决**: 检查 `api.py` 中的 `progress_callback` 设置

### 4. WebSocket 连接问题
- **检查点**: 查看前端是否成功建立 WebSocket 连接
- **原因**: WebSocket 连接可能断开或未建立
- **解决**: 检查前端控制台和后端日志中的 WebSocket 连接状态

## 调试步骤

### 1. 查看实时日志
```bash
# 实时查看后端日志
./view_backend_logs.sh

# 或者
tail -f mgx_backend/api.log
```

### 2. 运行代码生成任务
在前端运行一次代码生成任务，观察日志输出。

### 3. 检查关键日志点

#### a) stream_callback 是否被调用
查找日志中的：
```
🔍 [Stream] stream_callback called #1, chunk length: X, action: WriteCode
   progress_callback available: True/False
```

#### b) FILE: 标记是否被检测到
查找日志中的：
```
🔍 [Stream] WriteCode total FILE: markers in accumulated_content: X
   First few: ['FILE: ...', ...]
```

#### c) 文件是否被发送
查找日志中的：
```
📝 [Stream] New file detected: src/...
   ✅ [Stream] Sent file_update for: src/...
   📤 [Stream] Sent first file_content for: src/... (X chars)
```

### 4. 如果没有任何日志输出
- 检查 `stream_callback` 是否被正确传递到 `llm.ask()`
- 检查 `llm.py` 中的流式处理逻辑
- 检查是否有异常被捕获但没有输出

### 5. 如果 FILE: 标记没有被检测到
- 查看 `🔍 [Stream] WriteCode first X chars:` 输出，检查实际格式
- 可能需要调整 prompt 或解析逻辑

### 6. 如果 progress_callback 不可用
- 检查 `api.py` 中 `progress_callback` 的设置
- 检查 `team.run()` 是否正确传递了 `progress_callback`
- 检查 `context.kwargs` 的设置

## 当前代码逻辑

### WriteCode 流式处理流程

1. **stream_callback 被调用** (每次 LLM 返回一个 chunk)
   - 累积内容到 `accumulated_content`
   - 发送 `stream_chunk` 更新到前端

2. **检测 FILE: 标记**
   - 遍历 `accumulated_content` 的所有行
   - 查找以 `FILE:` 开头的完整行
   - 提取文件路径

3. **发送 file_update**
   - 检测到新文件时，发送 `file_update` 事件

4. **提取文件内容**
   - 使用正则表达式提取每个文件的内容
   - 发送 `file_content` 更新（每 50 字符或 0.3 秒）

5. **发送 file_complete**
   - 在 action 完成后，发送所有文件的 `file_complete` 事件

## 常见问题

### Q: 为什么日志中没有看到任何 WriteCode 相关的输出？
A: 可能的原因：
- `stream_callback` 没有被调用（检查 `llm.py`）
- 日志缓冲问题（已修复，使用 `-u` 参数）
- Engineer 的 action 没有执行（检查 `role.run()` 日志）

### Q: 为什么检测到了 FILE: 标记但没有发送文件？
A: 可能的原因：
- `progress_callback` 不可用（检查日志中的 `progress_callback available`）
- 正则表达式匹配失败（检查 `accumulated_content` 的实际格式）
- WebSocket 连接断开（检查前端控制台）

### Q: 为什么前端收到了 file_update 但没有收到 file_content？
A: 可能的原因：
- 内容提取失败（检查正则表达式匹配）
- 节流机制阻止了更新（检查 `last_file_update` 逻辑）
- 内容为空（检查 `file_content_raw` 的值）

## 下一步

运行一次代码生成任务，然后查看日志，根据上述检查点定位问题。

