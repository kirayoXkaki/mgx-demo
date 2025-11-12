# Agent 交互机制说明

## 概述

三个 Agent（ProductManager、Architect、Engineer）通过**消息总线（Message Bus）**机制进行交互，采用**观察者模式（Observer Pattern）**实现异步通信。

## 交互架构

```
┌─────────────────────────────────────────────────────────┐
│              Environment (消息总线)                      │
│  - 管理所有消息的发布和订阅                              │
│  - 维护消息历史记录                                      │
└─────────────────────────────────────────────────────────┘
                    ↑           ↑           ↑
                    │           │           │
        ┌───────────┘           │           └───────────┐
        │                       │                       │
┌───────▼────────┐    ┌─────────▼────────┐   ┌─────────▼────────┐
│ ProductManager │    │   Architect      │   │    Engineer       │
│                │    │                  │   │                   │
│ Watch:         │    │ Watch:           │   │ Watch:            │
│ UserRequirement│    │ WritePRD         │   │ WriteDesign       │
│                │    │                  │   │                   │
│ Action:        │    │ Action:          │   │ Action:           │
│ WritePRD       │    │ WriteDesign      │   │ WriteCode         │
└────────────────┘    └──────────────────┘   └───────────────────┘
```

## 交互流程

### 1. 初始化阶段

```python
# 创建团队和环境
team = Team()
team.hire([ProductManager(), Architect(), Engineer()])

# 每个角色设置监听的消息类型
ProductManager.watch({"UserRequirement"})  # 监听用户需求
Architect.watch({"WritePRD"})              # 监听PRD完成消息
Engineer.watch({"WriteDesign"})            # 监听设计完成消息
```

### 2. 消息发布流程

#### Round 1: ProductManager
```
User Input: "Create a 2048 game"
    ↓
Environment.publish_message(UserRequirement)
    ↓
所有角色 observe() 接收消息
    ↓
ProductManager 检测到 UserRequirement (在 watch 列表中)
    ↓
ProductManager._news.append(message)  # 添加到待处理队列
    ↓
ProductManager.think() → 决定执行 WritePRD
    ↓
ProductManager.act() → 执行 WritePRD action
    ↓
生成 PRD 内容
    ↓
创建 Message(cause_by="WritePRD", content=PRD内容)
    ↓
Environment.publish_message(PRD Message)  # 发布到消息总线
```

#### Round 2: Architect
```
Environment.publish_message(PRD Message)
    ↓
所有角色 observe() 接收消息
    ↓
Architect 检测到 WritePRD (在 watch 列表中)
    ↓
Architect._news.append(message)
    ↓
Architect.think() → 决定执行 WriteDesign
    ↓
Architect.act() → 执行 WriteDesign action
    ↓
读取 PRD 内容作为 context
    ↓
生成 System Design 内容
    ↓
创建 Message(cause_by="WriteDesign", content=Design内容)
    ↓
Environment.publish_message(Design Message)
```

#### Round 3: Engineer
```
Environment.publish_message(Design Message)
    ↓
所有角色 observe() 接收消息
    ↓
Engineer 检测到 WriteDesign (在 watch 列表中)
    ↓
Engineer._news.append(message)
    ↓
Engineer.think() → 决定执行 WriteCode
    ↓
Engineer.act() → 执行 WriteCode action
    ↓
读取 Design 内容作为 context
    ↓
生成代码文件
    ↓
创建 Message(cause_by="WriteCode", content=代码内容)
    ↓
Environment.publish_message(Code Message)
```

## 核心代码机制

### 1. 消息总线 (Environment)

```python
class Environment:
    def publish_message(self, message: Message):
        """发布消息到所有角色"""
        self.history.append(message)
        
        # 通知所有角色
        for role in self.roles.values():
            await role.observe(message)
```

### 2. 消息观察 (Role.observe)

```python
async def observe(self, message: Message):
    """观察消息"""
    # 检查是否应该响应此消息
    if not self._watch or message.cause_by in self._watch:
        self._news.append(message)  # 添加到待处理队列
```

### 3. 消息处理 (Role.run)

```python
async def run(self):
    """运行角色（think + act）"""
    if await self.think():  # 检查是否有待处理消息
        message = await self.act()  # 执行action
        if message and self._env:
            await self._env.publish_message(message)  # 发布新消息
```

## 交互特点

### ✅ 优点

1. **解耦**: 角色之间不直接依赖，通过消息总线通信
2. **可扩展**: 容易添加新角色和消息类型
3. **异步**: 支持异步消息处理
4. **可追踪**: 所有消息都保存在 `history` 中

### ⚠️ 当前限制

1. **单向流程**: 目前是线性的单向流程（User → PM → Arch → Eng）
2. **无反馈机制**: Engineer 完成后不会反馈给 PM 或 Architect
3. **无并行处理**: 角色按顺序执行，不支持并行
4. **无协商机制**: 角色之间无法协商或讨论

## 消息格式

```python
class Message:
    content: str          # 消息内容（PRD/Design/Code）
    role: str            # 发送者角色名称
    cause_by: str        # 触发此消息的action类型
    sent_from: str       # 发送者
    send_to: str        # 接收者（可选）
    timestamp: datetime  # 时间戳
    metadata: dict      # 元数据
```

## 实际交互示例

```python
# 1. 用户输入
UserRequirement(content="Create a 2048 game")
    ↓
# 2. ProductManager 处理
Message(
    content="[PRD内容]",
    role="Alice",
    cause_by="WritePRD"
)
    ↓
# 3. Architect 处理
Message(
    content="[System Design内容]",
    role="Bob",
    cause_by="WriteDesign"
)
    ↓
# 4. Engineer 处理
Message(
    content="FILE: src/index.html\n---\n[代码内容]",
    role="Charlie",
    cause_by="WriteCode"
)
```

## 总结

**是的，三个 Agent 之间存在交互**，通过以下机制：

1. **消息总线**: Environment 作为中央消息分发器
2. **观察者模式**: 每个角色监听特定类型的消息
3. **链式反应**: UserRequirement → WritePRD → WriteDesign → WriteCode
4. **异步处理**: 消息通过异步方式传递和处理

这种设计使得系统具有良好的可扩展性和解耦性，但目前的实现是线性的单向流程，不支持复杂的多轮对话或协商机制。

