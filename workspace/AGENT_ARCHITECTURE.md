# 智能体架构与工作原理

## 核心概念

### 1. Environment（环境/消息总线）

**Environment** 是智能体系统的核心通信机制，采用**发布-订阅模式（Pub-Sub）**。

```python
class Environment:
    context: Context          # 全局上下文（配置、成本管理、LLM等）
    roles: Dict[str, Role]   # 注册的所有角色
    history: List[Message]   # 消息历史记录
```

#### 核心功能

1. **消息发布** (`publish_message`)
   ```python
   async def publish_message(self, message: Message):
       self.history.append(message)  # 保存到历史
       for role in self.roles.values():
           await role.observe(message)  # 通知所有角色
   ```

2. **角色管理** (`add_roles`)
   - 注册角色到环境
   - 为角色设置环境引用

3. **执行轮次** (`run`)
   - 遍历所有角色
   - 执行非空闲角色的 `run()` 方法

4. **空闲检测** (`is_idle`)
   - 检查所有角色是否都空闲
   - 用于判断项目是否完成

### 2. Role（角色/智能体）

**Role** 是智能体的基础类，实现了**观察-思考-行动（Observe-Think-Act）**模式。

```python
class Role:
    name: str                    # 角色名称（如 "Alice", "Bob", "Charlie"）
    profile: str                 # 角色描述
    goal: str                    # 目标
    constraints: str             # 约束条件
    actions: List[Action]        # 可执行的动作列表
    _watch: Set[str]            # 监听的消息类型
    _env: Environment            # 所属环境
    _llm: BaseLLM               # LLM 实例
    _news: List[Message]        # 待处理的消息队列
    _todo: Optional[Action]     # 当前待执行的动作
```

#### 核心方法

##### 1. `observe(message)` - 观察消息
```python
async def observe(self, message: Message):
    # 检查是否应该响应此消息
    if not self._watch or message.cause_by in self._watch:
        self._news.append(message)  # 添加到待处理队列
```

**工作原理**：
- 每个角色通过 `watch()` 设置监听的消息类型
- 当 Environment 发布消息时，所有角色都会收到
- 只有监听了该消息类型的角色才会将其加入 `_news` 队列

##### 2. `think()` - 思考下一步
```python
async def think(self) -> bool:
    if not self._news:
        return False  # 没有待处理消息，不执行
    
    # 发送思考状态更新
    await callback({"type": "thinking", ...})
    
    # 简单策略：按顺序执行第一个动作
    if self.actions:
        self._todo = self.actions[0]
        await callback({"type": "action_start", ...})
        return True
    
    return False
```

**工作原理**：
- 检查是否有待处理消息（`_news`）
- 如果有，选择要执行的动作（当前是简单策略：第一个动作）
- 设置 `_todo` 为待执行的动作
- 返回 `True` 表示可以执行

##### 3. `act()` - 执行动作
```python
async def act(self) -> Message:
    if not self._todo:
        return None
    
    # 发送执行状态更新
    await callback({"type": "action_executing", ...})
    
    # 准备上下文（从 _news 中提取）
    context = "\n".join([msg.content for msg in self._news])
    
    # 执行动作（调用 LLM）
    result = await self._todo.run(context, stream_callback=stream_callback)
    
    # 创建输出消息
    message = Message(
        content=result,
        role=self.name,
        cause_by=self._todo.name
    )
    
    # 清空待处理消息和待执行动作
    self._news = []
    self._todo = None
    
    return message
```

**工作原理**：
- 使用 `_news` 中的消息内容作为上下文
- 调用 `_todo.run()` 执行动作（通常调用 LLM）
- 将执行结果封装为 Message
- 清空 `_news` 和 `_todo`，标记角色为空闲

##### 4. `run()` - 运行角色（组合 think + act）
```python
async def run(self) -> Optional[Message]:
    if await self.think():  # 思考：决定是否执行
        message = await self.act()  # 行动：执行动作
        if message and self._env:
            await self._env.publish_message(message)  # 发布结果消息
        return message
    return None
```

**工作流程**：
1. `think()` - 检查是否有待处理消息，决定执行哪个动作
2. `act()` - 执行动作，生成结果
3. `publish_message()` - 将结果发布到 Environment

### 3. Team（团队）

**Team** 管理多个角色，协调整个工作流程。

```python
class Team:
    env: Environment      # 环境（消息总线）
    investment: float      # 预算
    idea: str             # 项目想法
```

#### 核心方法

##### `run()` - 运行团队协作
```python
async def run(self, n_round: int = 5, idea: str = "", progress_callback=None):
    # 1. 发布初始消息（用户需求）
    message = UserRequirement(content=idea)
    await self.env.publish_message(message)
    
    # 2. 设置进度回调
    if progress_callback:
        self.env.context.kwargs.set("progress_callback", progress_callback)
    
    # 3. 循环执行轮次
    round_num = 0
    while n_round > 0:
        if self.env.is_idle:  # 所有角色都空闲，项目完成
            break
        
        n_round -= 1
        round_num += 1
        
        # 检查预算
        self._check_balance()
        
        # 执行一轮（所有非空闲角色执行一次）
        await self.env.run()
        
        # 打印成本信息
        print(f"💵 Cost: ${cost_manager.total_cost:.4f}")
    
    return self.env.history  # 返回所有消息历史
```

## 完整工作流程

### 初始化阶段

```
1. 创建 Team
   team = Team(context=ctx)
   
2. 创建 Environment（Team 内部自动创建）
   env = Environment(context=ctx)
   
3. 雇佣角色
   team.hire([ProductManager(), Architect(), Engineer()])
   → env.add_roles([...])
   → 每个角色调用 role.set_env(env)
   
4. 设置监听
   ProductManager.watch({"UserRequirement"})
   Architect.watch({"WritePRD"})
   Engineer.watch({"WriteDesign"})
```

### 执行阶段（一轮）

```
Round 1:
┌─────────────────────────────────────────┐
│ 1. Team.run() 发布 UserRequirement     │
│    → env.publish_message(message)      │
│    → 所有角色 observe(message)          │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 2. Environment.run()                    │
│    for role in roles:                    │
│        if not role.is_idle:              │
│            await role.run()              │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 3. ProductManager.run()                │
│    → think()                            │
│       - 检查 _news (有 UserRequirement) │
│       - 设置 _todo = WritePRD           │
│    → act()                              │
│       - 执行 WritePRD                   │
│       - 生成 PRD 内容                   │
│       - 创建 Message(cause_by="WritePRD")│
│    → env.publish_message(PRD Message)  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 4. 所有角色 observe(PRD Message)       │
│    - Architect 检测到 WritePRD          │
│    - 将消息加入 _news                   │
└─────────────────────────────────────────┘

Round 2:
┌─────────────────────────────────────────┐
│ 5. Architect.run()                     │
│    → think()                            │
│       - 检查 _news (有 WritePRD)        │
│       - 设置 _todo = WriteDesign        │
│    → act()                              │
│       - 执行 WriteDesign                │
│       - 生成 Design 内容                │
│       - 创建 Message(cause_by="WriteDesign")│
│    → env.publish_message(Design Message)│
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 6. 所有角色 observe(Design Message)    │
│    - Engineer 检测到 WriteDesign        │
│    - 将消息加入 _news                   │
└─────────────────────────────────────────┘

Round 3:
┌─────────────────────────────────────────┐
│ 7. Engineer.run()                      │
│    → think()                            │
│       - 检查 _news (有 WriteDesign)     │
│       - 设置 _todo = WriteCode          │
│    → act()                              │
│       - 执行 WriteCode                  │
│       - 生成 Code 内容                   │
│       - 创建 Message(cause_by="WriteCode")│
│    → env.publish_message(Code Message)  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 8. 所有角色 observe(Code Message)      │
│    - 没有角色监听 WriteCode             │
│    - 所有角色 _news 为空                │
│    - env.is_idle = True                 │
│    - 项目完成！                          │
└─────────────────────────────────────────┘
```

## 关键设计模式

### 1. 发布-订阅模式（Pub-Sub）

- **发布者**: Environment (`publish_message`)
- **订阅者**: Roles (`observe`)
- **消息类型**: 通过 `_watch` 过滤

### 2. 观察者模式（Observer）

- **被观察者**: Environment
- **观察者**: Roles
- **通知机制**: `observe()` 方法

### 3. 状态机模式

每个 Role 的状态：
```
IDLE (空闲)
  ↓ (收到消息)
HAS_NEWS (有待处理消息)
  ↓ (think())
HAS_TODO (有待执行动作)
  ↓ (act())
EXECUTING (执行中)
  ↓ (完成)
IDLE (空闲)
```

### 4. 责任链模式

消息传递链：
```
UserRequirement → ProductManager → WritePRD → Architect → WriteDesign → Engineer → WriteCode
```

## 数据流

### 消息流

```
User Input
    ↓
UserRequirement Message
    ↓
Environment.publish_message()
    ↓
所有 Role.observe()
    ↓
匹配的 Role._news.append()
    ↓
Role.think() → Role.act()
    ↓
生成新 Message
    ↓
Environment.publish_message()
    ↓
... (循环)
```

### 状态流

```
Role State:
  _news: []           → 收到消息 → _news: [Message]
  _todo: None         → think()  → _todo: Action
  is_idle: True       →          → is_idle: False
                        act()     → _news: []
                       完成       → _todo: None
                                   → is_idle: True
```

## 关键属性

### Role.is_idle

```python
@property
def is_idle(self) -> bool:
    return len(self._news) == 0 and self._todo is None
```

- **True**: 角色空闲，没有待处理消息，没有待执行动作
- **False**: 角色忙碌，有待处理消息或待执行动作

### Environment.is_idle

```python
@property
def is_idle(self) -> bool:
    return all(role.is_idle for role in self.roles.values())
```

- **True**: 所有角色都空闲，项目完成
- **False**: 至少有一个角色忙碌，继续执行

## 实际示例

### 代码执行流程

```python
# 1. 创建团队
team = Team(context=ctx)
team.hire([ProductManager(), Architect(), Engineer()])
team.invest(10.0)

# 2. 运行项目
history = await team.run(n_round=5, idea="Create a 2048 game")

# 内部执行流程：
# Round 1:
#   - UserRequirement 发布
#   - ProductManager 接收 → 执行 WritePRD → 发布 PRD Message
# Round 2:
#   - Architect 接收 PRD → 执行 WriteDesign → 发布 Design Message
# Round 3:
#   - Engineer 接收 Design → 执行 WriteCode → 发布 Code Message
# Round 4:
#   - 所有角色空闲 → env.is_idle = True → 项目完成
```

## 总结

1. **Environment** = 消息总线，负责消息分发和角色协调
2. **Role** = 智能体，实现观察-思考-行动循环
3. **Team** = 团队管理器，控制整体工作流程
4. **Message** = 通信载体，在角色之间传递信息
5. **Action** = 具体任务，由 Role 执行（通常调用 LLM）

整个系统通过**消息驱动**的方式实现多智能体协作，每个角色独立工作，通过消息总线进行通信。

