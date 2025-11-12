# 智能体工作流程图解

## 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        Team (团队)                           │
│  - 管理多个角色                                              │
│  - 控制工作流程                                              │
│  - 预算管理                                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Environment (环境)                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Message Bus (消息总线)                              │   │
│  │  - history: [Message1, Message2, ...]                │   │
│  │  - roles: {name: Role}                                │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
         │              │              │
         ↓              ↓              ↓
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ ProductMgr   │ │  Architect   │ │  Engineer    │
│ (Alice)      │ │  (Bob)       │ │  (Charlie)  │
│              │ │              │ │              │
│ watch:       │ │ watch:       │ │ watch:       │
│ UserRequire  │ │ WritePRD     │ │ WriteDesign │
│              │ │              │ │              │
│ action:      │ │ action:      │ │ action:      │
│ WritePRD    │ │ WriteDesign  │ │ WriteCode   │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 详细工作流程

### 阶段 1: 初始化

```
┌─────────────────┐
│ 创建 Team       │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 创建 Environment│
│ (消息总线)      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 雇佣角色        │
│ - ProductManager│
│ - Architect     │
│ - Engineer      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 设置监听        │
│ PM → UserRequire│
│ Arch → WritePRD │
│ Eng → WriteDesign│
└─────────────────┘
```

### 阶段 2: 执行循环

```
┌─────────────────────────────────────────────────────────┐
│                    Round 1                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  1. Team.run()                                          │
│     └─> env.publish_message(UserRequirement)           │
│         └─> 所有角色 observe()                           │
│             ├─> PM: _news.append() ✓                    │
│             ├─> Arch: 不匹配，忽略                        │
│             └─> Eng: 不匹配，忽略                        │
│                                                          │
│  2. env.run()                                           │
│     └─> 遍历所有角色                                     │
│         └─> PM.run() (非空闲)                            │
│             ├─> think()                                  │
│             │   └─> _todo = WritePRD                    │
│             ├─> act()                                    │
│             │   ├─> 调用 LLM (WritePRD)                  │
│             │   ├─> 生成 PRD 内容                        │
│             │   └─> 创建 Message(cause_by="WritePRD")   │
│             └─> env.publish_message(PRD Message)         │
│                 └─> 所有角色 observe()                   │
│                     ├─> PM: 不匹配，忽略                  │
│                     ├─> Arch: _news.append() ✓            │
│                     └─> Eng: 不匹配，忽略                  │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    Round 2                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  3. env.run()                                           │
│     └─> Arch.run() (非空闲)                              │
│         ├─> think()                                      │
│         │   └─> _todo = WriteDesign                      │
│         ├─> act()                                        │
│         │   ├─> 调用 LLM (WriteDesign)                  │
│         │   ├─> 生成 Design 内容                        │
│         │   └─> 创建 Message(cause_by="WriteDesign")    │
│         └─> env.publish_message(Design Message)         │
│             └─> 所有角色 observe()                       │
│                 ├─> PM: 不匹配，忽略                      │
│                 ├─> Arch: 不匹配，忽略                    │
│                 └─> Eng: _news.append() ✓                 │
│                                                          │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    Round 3                              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  4. env.run()                                           │
│     └─> Eng.run() (非空闲)                               │
│         ├─> think()                                      │
│         │   └─> _todo = WriteCode                         │
│         ├─> act()                                        │
│         │   ├─> 调用 LLM (WriteCode)                     │
│         │   ├─> 生成 Code 内容（流式）                   │
│         │   └─> 创建 Message(cause_by="WriteCode")      │
│         └─> env.publish_message(Code Message)           │
│             └─> 所有角色 observe()                       │
│                 └─> 没有角色监听 WriteCode               │
│                     └─> 所有角色 _news = []              │
│                         └─> env.is_idle = True ✓         │
│                                                          │
│  5. Team.run() 检测到 env.is_idle = True                │
│     └─> 项目完成！                                        │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Role 内部状态机

```
                    ┌─────────┐
                    │  IDLE   │
                    │         │
                    │ _news=[]│
                    │_todo=None│
                    └────┬────┘
                         │
                         │ Environment.publish_message()
                         │ message.cause_by in _watch
                         ↓
                    ┌─────────┐
                    │ HAS_NEWS│
                    │         │
                    │_news=[M]│
                    │_todo=None│
                    └────┬────┘
                         │
                         │ think()
                         │ 选择 action
                         ↓
                    ┌─────────┐
                    │ HAS_TODO│
                    │         │
                    │_news=[M]│
                    │_todo=Act│
                    └────┬────┘
                         │
                         │ act()
                         │ 执行动作
                         ↓
                    ┌─────────┐
                    │EXECUTING│
                    │         │
                    │ 调用 LLM │
                    │ 生成结果 │
                    └────┬────┘
                         │
                         │ 完成
                         │ _news=[]
                         │ _todo=None
                         ↓
                    ┌─────────┐
                    │  IDLE   │
                    └─────────┘
```

## 消息传递示例

```
时间线：

T0: User Input "Create a 2048 game"
    ↓
T1: UserRequirement Message
    ├─> Environment.publish_message()
    ├─> PM.observe() → _news.append() ✓
    ├─> Arch.observe() → 忽略（不在 watch 中）
    └─> Eng.observe() → 忽略（不在 watch 中）

T2: PM.run()
    ├─> think() → _todo = WritePRD
    ├─> act() → 调用 LLM，生成 PRD
    └─> Message(cause_by="WritePRD", content="[PRD内容]")
        └─> Environment.publish_message()

T3: WritePRD Message
    ├─> PM.observe() → 忽略
    ├─> Arch.observe() → _news.append() ✓
    └─> Eng.observe() → 忽略

T4: Arch.run()
    ├─> think() → _todo = WriteDesign
    ├─> act() → 调用 LLM，生成 Design
    └─> Message(cause_by="WriteDesign", content="[Design内容]")
        └─> Environment.publish_message()

T5: WriteDesign Message
    ├─> PM.observe() → 忽略
    ├─> Arch.observe() → 忽略
    └─> Eng.observe() → _news.append() ✓

T6: Eng.run()
    ├─> think() → _todo = WriteCode
    ├─> act() → 调用 LLM，生成 Code（流式）
    └─> Message(cause_by="WriteCode", content="[Code内容]")
        └─> Environment.publish_message()

T7: WriteCode Message
    └─> 所有角色 observe() → 都忽略（没有角色监听）

T8: env.is_idle = True → 项目完成
```

## 关键代码路径

### 1. 消息发布路径

```
Team.run()
  → env.publish_message(message)
    → for role in roles:
        → role.observe(message)
          → if message.cause_by in _watch:
              → _news.append(message)
```

### 2. 角色执行路径

```
Environment.run()
  → for role in roles:
      → if not role.is_idle:
          → role.run()
            → think()
              → if _news:
                  → _todo = actions[0]
                  → return True
            → act()
              → context = "\n".join(_news)
              → result = _todo.run(context)
              → message = Message(...)
              → _news = []
              → _todo = None
            → env.publish_message(message)
```

### 3. 空闲检测路径

```
Team.run()
  → while n_round > 0:
      → if env.is_idle:
          → break
      → env.run()
        → for role in roles:
            → if not role.is_idle:
                → role.run()

env.is_idle
  → all(role.is_idle for role in roles)
    → all(len(role._news) == 0 and role._todo is None)
```

## 总结

1. **Environment** 是消息总线，所有通信都通过它
2. **Role** 通过 `watch()` 订阅感兴趣的消息类型
3. **Role** 通过 `observe()` 接收消息，加入 `_news` 队列
4. **Role** 通过 `think()` 决定执行哪个动作
5. **Role** 通过 `act()` 执行动作，生成结果消息
6. **Role** 通过 `run()` 组合 think + act，并发布结果
7. **Team** 通过轮次循环协调整个流程
8. **is_idle** 机制用于判断项目是否完成

整个系统是**事件驱动**的，通过消息传递实现多智能体协作。

