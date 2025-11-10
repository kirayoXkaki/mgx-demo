# MetaGPT 后端架构分析文档

## 1. 概述

MetaGPT 是一个多智能体框架,通过模拟软件公司的角色协作来自动生成完整的软件项目。核心功能是通过 `generate_repo` 函数接收需求描述,然后由多个AI角色协作完成从需求分析到代码实现的全流程。

## 2. 核心架构设计

### 2.1 架构层次

```
用户需求 (idea)
    ↓
generate_repo() 函数
    ↓
Context + Config (配置管理)
    ↓
Team (团队管理)
    ↓
Environment (消息环境)
    ↓
Roles (多个AI角色)
    ↓
Actions (具体行为)
    ↓
LLM Provider (大语言模型)
    ↓
ProjectRepo (项目仓库输出)
```

### 2.2 核心组件关系图

```
┌─────────────────────────────────────────────────────────┐
│                    generate_repo()                       │
│  - 入口函数                                              │
│  - 初始化配置和上下文                                     │
│  - 创建团队并分配角色                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│                      Team                                │
│  - 管理多个Role                                          │
│  - 协调角色间通信                                        │
│  - 控制工作流程                                          │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        ↓            ↓            ↓
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Product  │  │Architect │  │ Engineer │
│ Manager  │  │          │  │          │
└──────────┘  └──────────┘  └──────────┘
      │             │             │
      ↓             ↓             ↓
┌──────────┐  ┌──────────┐  ┌──────────┐
│ WritePRD │  │WriteDesign│ │WriteCode │
└──────────┘  └──────────┘  └──────────┘
```

## 3. 关键模块详解

### 3.1 generate_repo() 函数

**位置**: `metagpt/software_company.py`

**核心功能**:
- 作为整个系统的入口点
- 初始化配置和上下文
- 创建团队并雇佣角色
- 启动异步工作流
- 返回项目路径

**函数签名**:
```python
def generate_repo(
    idea,                      # 用户需求描述
    investment=3.0,            # 投资金额(控制token使用)
    n_round=5,                 # 运行轮数
    code_review=True,          # 是否启用代码审查
    run_tests=False,           # 是否运行测试
    implement=True,            # 是否实现代码
    project_name="",           # 项目名称
    inc=False,                 # 增量模式
    project_path="",           # 项目路径
    reqa_file="",              # 质量保证文件
    max_auto_summarize_code=0, # 代码总结次数
    recover_path=None,         # 恢复路径
)
```

**工作流程**:
```python
# 1. 更新配置
config.update_via_cli(project_path, project_name, inc, reqa_file, max_auto_summarize_code)

# 2. 创建上下文
ctx = Context(config=config)

# 3. 创建团队
company = Team(context=ctx)

# 4. 雇佣角色
company.hire([
    TeamLeader(),
    ProductManager(),
    Architect(),
    Engineer2(),
    DataAnalyst(),
])

# 5. 投资(设置预算)
company.invest(investment)

# 6. 运行团队
asyncio.run(company.run(n_round=n_round, idea=idea))

# 7. 返回项目路径
return ctx.kwargs.get("project_path")
```

### 3.2 Context 类

**位置**: `metagpt/context.py`

**核心功能**:
- 管理全局配置
- 管理LLM实例
- 管理成本追踪
- 提供共享状态

**关键属性**:
```python
class Context(BaseModel):
    kwargs: AttrDict           # 动态属性字典
    config: Config             # 配置对象
    cost_manager: CostManager  # 成本管理器
    _llm: Optional[BaseLLM]    # LLM实例
```

### 3.3 Team 类

**位置**: `metagpt/team.py`

**核心功能**:
- 管理多个Role实例
- 提供Environment进行消息传递
- 控制工作流程和轮次
- 序列化和反序列化团队状态

**关键方法**:
```python
class Team(BaseModel):
    env: Optional[Environment]  # 环境(消息总线)
    investment: float           # 投资金额
    idea: str                   # 需求描述
    
    def hire(self, roles: list[Role]):
        """雇佣角色"""
        self.env.add_roles(roles)
    
    def invest(self, investment: float):
        """设置投资"""
        self.investment = investment
        self.cost_manager.max_budget = investment
    
    async def run(self, n_round=5, idea=""):
        """运行团队协作"""
        # 发布需求到环境
        # 循环运行n_round轮
        # 每轮让角色依次思考和行动
```

### 3.4 Role 基类

**位置**: `metagpt/roles/role.py`

**核心功能**:
- 定义角色的基本行为模式
- 管理角色的Actions
- 实现思考-行动循环
- 处理消息订阅

**关键属性和方法**:
```python
class Role(BaseModel):
    name: str                    # 角色名称
    profile: str                 # 角色简介
    goal: str                    # 角色目标
    constraints: str             # 约束条件
    actions: list[Action]        # 可执行的动作
    
    def _watch(self, actions):
        """订阅特定动作的输出"""
        
    async def _think(self):
        """思考下一步做什么"""
        
    async def _act(self):
        """执行动作"""
        
    async def run(self, message):
        """运行角色(思考+行动)"""
```

### 3.5 具体角色实现

#### 3.5.1 ProductManager (产品经理)

**位置**: `metagpt/roles/product_manager.py`

**职责**:
- 分析用户需求
- 编写PRD(产品需求文档)
- 进行市场调研和竞品分析

**核心Actions**:
- `PrepareDocuments`: 准备文档
- `WritePRD`: 编写PRD

**工作流程**:
```python
class ProductManager(RoleZero):
    name: str = "Alice"
    profile: str = "Product Manager"
    goal: str = "Create a Product Requirement Document"
    
    def __init__(self):
        self.set_actions([PrepareDocuments, WritePRD])
        self._watch([UserRequirement, PrepareDocuments])
```

#### 3.5.2 Architect (架构师)

**位置**: `metagpt/roles/architect.py`

**职责**:
- 设计系统架构
- 选择技术栈
- 输出系统设计文档

**核心Actions**:
- `WriteDesign`: 编写设计文档

**工作流程**:
```python
class Architect(RoleZero):
    name: str = "Bob"
    profile: str = "Architect"
    goal: str = "design a concise, usable, complete software system"
    
    def __init__(self):
        self.set_actions([WriteDesign])
        self._watch({WritePRD})  # 监听PRD完成
```

#### 3.5.3 Engineer2 (工程师)

**位置**: `metagpt/roles/engineer2.py`

**职责**:
- 根据设计文档编写代码
- 实现具体功能
- 进行代码审查

**核心Actions**:
- `WriteCode`: 编写代码
- `WriteCodeReview`: 代码审查

### 3.6 Environment (环境)

**位置**: `metagpt/environment/base_env.py`

**核心功能**:
- 作为消息总线
- 管理角色间的通信
- 维护消息历史

**关键方法**:
```python
class Environment(BaseModel):
    roles: dict[str, Role]  # 角色字典
    
    def add_roles(self, roles: list[Role]):
        """添加角色到环境"""
        
    async def publish_message(self, message: Message):
        """发布消息"""
        
    def get_roles(self) -> list[Role]:
        """获取所有角色"""
```

### 3.7 ProjectRepo 类

**位置**: `metagpt/utils/project_repo.py`

**核心功能**:
- 管理项目文件结构
- 提供文档和代码的访问接口
- 支持Git仓库操作

**类结构**:
```python
class ProjectRepo(FileRepository):
    def __init__(self, root: str | Path | GitRepository):
        self._git_repo = git_repo_
        self.docs = DocFileRepositories(self._git_repo)      # 文档仓库
        self.resources = ResourceFileRepositories(self._git_repo)  # 资源仓库
        self.tests = ...                                      # 测试仓库
        self.test_outputs = ...                               # 测试输出
        
    @property
    async def requirement(self):
        """获取需求文档"""
        return await self.docs.get(filename=REQUIREMENT_FILENAME)
    
    @property
    def git_repo(self) -> GitRepository:
        """获取Git仓库"""
        return self._git_repo
    
    @property
    def srcs(self) -> FileRepository:
        """获取源代码仓库"""
        return self._git_repo.new_file_repository(relative_path=self._srcs_path)
```

**文件组织结构**:
```
project_root/
├── docs/                    # 文档目录
│   ├── prd/                # PRD文档
│   ├── system_design/      # 系统设计
│   ├── tasks/              # 任务分解
│   └── code_summary/       # 代码总结
├── resources/              # 资源目录
│   ├── competitive_analysis/
│   ├── data_api_design/
│   └── seq_flow/
├── src/                    # 源代码
├── tests/                  # 测试代码
└── test_outputs/           # 测试输出
```

## 4. LLM集成方式

### 4.1 LLM Provider架构

**位置**: `metagpt/provider/`

**核心组件**:
- `BaseLLM`: LLM基类
- `OpenAILLM`: OpenAI实现
- `LLMProviderRegistry`: LLM提供商注册表

### 4.2 配置方式

**配置文件**: `config/config2.yaml`

```yaml
llm:
  api_type: "openai"
  model: "gpt-4-turbo"
  base_url: "https://api.openai.com/v1"
  api_key: "YOUR_API_KEY"
```

### 4.3 使用方式

```python
from metagpt.config2 import config
from metagpt.context import Context

# 1. 通过配置创建上下文
ctx = Context(config=config)

# 2. 获取LLM实例
llm = ctx.llm

# 3. 调用LLM
response = await llm.aask(prompt="Your prompt here")
```

### 4.4 成本管理

```python
class CostManager:
    """管理API调用成本"""
    total_prompt_tokens: int = 0
    total_completion_tokens: int = 0
    total_cost: float = 0.0
    max_budget: float = 10.0
    
    def update_cost(self, prompt_tokens, completion_tokens, model):
        """更新成本"""
        # 根据模型计算成本
        # 检查是否超出预算
```

## 5. 完整工作流程

### 5.1 端到端流程图

```
用户输入: "Create a 2048 game"
    ↓
[1] generate_repo() 初始化
    - 创建Context和Config
    - 设置项目路径
    ↓
[2] 创建Team并雇佣角色
    - TeamLeader
    - ProductManager
    - Architect
    - Engineer2
    - DataAnalyst
    ↓
[3] 发布UserRequirement到Environment
    ↓
[4] ProductManager响应
    - 执行PrepareDocuments
    - 执行WritePRD
    - 输出: PRD文档
    ↓
[5] Architect响应
    - 读取PRD
    - 执行WriteDesign
    - 输出: 系统设计文档
    ↓
[6] Engineer2响应
    - 读取系统设计
    - 执行WriteCode
    - 输出: 源代码文件
    ↓
[7] 可选: QA Engineer
    - 编写测试
    - 运行测试
    ↓
[8] 保存到ProjectRepo
    - 文档保存到docs/
    - 代码保存到src/
    - 提交到Git
    ↓
[9] 返回项目路径
```

### 5.2 消息流转机制

```python
# 1. 发布消息
message = Message(
    content="Create a 2048 game",
    role="User",
    cause_by=UserRequirement
)
await env.publish_message(message)

# 2. 角色订阅和响应
class ProductManager(Role):
    def __init__(self):
        self._watch([UserRequirement])  # 订阅UserRequirement
        
    async def _think(self):
        # 检查是否有新消息
        if self.rc.news:
            # 决定执行哪个Action
            self.rc.todo = WritePRD()
            
    async def _act(self):
        # 执行Action
        result = await self.rc.todo.run(context)
        # 发布新消息
        msg = Message(content=result, cause_by=WritePRD)
        await self.publish_message(msg)
```

## 6. 可复用代码片段

### 6.1 基础框架搭建

```python
import asyncio
from metagpt.config2 import Config
from metagpt.context import Context
from metagpt.team import Team
from metagpt.roles import ProductManager, Architect, Engineer2

async def create_software_company(idea: str, api_key: str):
    """创建软件公司并生成项目"""
    
    # 1. 配置LLM
    config = Config.default()
    config.llm.api_key = api_key
    config.llm.model = "gpt-4-turbo"
    
    # 2. 创建上下文
    ctx = Context(config=config)
    
    # 3. 创建团队
    company = Team(context=ctx)
    
    # 4. 雇佣角色
    company.hire([
        ProductManager(),
        Architect(),
        Engineer2(),
    ])
    
    # 5. 设置预算
    company.invest(investment=5.0)
    
    # 6. 运行
    await company.run(n_round=5, idea=idea)
    
    # 7. 返回结果
    return ctx.kwargs.get("project_path")

# 使用
project_path = asyncio.run(
    create_software_company(
        idea="Create a 2048 game",
        api_key="your-api-key"
    )
)
print(f"Project created at: {project_path}")
```

### 6.2 自定义角色

```python
from metagpt.roles.role import Role
from metagpt.actions import Action

class CustomAction(Action):
    """自定义动作"""
    
    async def run(self, context: str) -> str:
        # 构建prompt
        prompt = f"Based on: {context}\nDo something..."
        
        # 调用LLM
        response = await self.llm.aask(prompt)
        
        return response

class CustomRole(Role):
    """自定义角色"""
    
    name: str = "CustomRole"
    profile: str = "Custom Role"
    goal: str = "Do custom tasks"
    
    def __init__(self):
        super().__init__()
        self.set_actions([CustomAction])
        self._watch([SomeOtherAction])  # 订阅其他动作
```

### 6.3 配置管理

```python
from metagpt.config2 import Config

# 方式1: 从YAML加载
config = Config.from_yaml("config/config2.yaml")

# 方式2: 代码配置
config = Config.default()
config.llm.api_key = "your-key"
config.llm.model = "gpt-4"
config.llm.base_url = "https://api.openai.com/v1"

# 方式3: 环境变量
# export OPENAI_API_KEY="your-key"
config = Config.default()  # 自动读取环境变量
```

### 6.4 项目仓库操作

```python
from metagpt.utils.project_repo import ProjectRepo
from pathlib import Path

# 创建项目仓库
repo = ProjectRepo(root="/path/to/project")

# 读取需求
requirement = await repo.requirement

# 访问文档
prd_files = repo.docs.prd.all_files
design_files = repo.docs.system_design.all_files

# 访问源代码
src_files = repo.srcs.all_files

# 写入文件
await repo.docs.prd.save(
    filename="prd.md",
    content="# Product Requirements\n..."
)

# Git操作
repo.git_repo.add_change({"file.py": "content"})
repo.git_repo.commit("Add new feature")
```

### 6.5 成本控制

```python
from metagpt.context import Context

ctx = Context()

# 设置最大预算
ctx.cost_manager.max_budget = 5.0

# 检查成本
print(f"Total cost: ${ctx.cost_manager.total_cost}")
print(f"Tokens used: {ctx.cost_manager.total_prompt_tokens}")

# 成本超限会抛出异常
try:
    await some_expensive_operation()
except NoMoneyException:
    print("Budget exceeded!")
```

## 7. 复刻实现建议

### 7.1 最小可行实现(MVP)

**第一阶段: 核心框架**
1. 实现Config和Context管理
2. 实现基础的LLM调用封装
3. 实现简单的Role和Action基类
4. 实现基础的消息传递机制

**第二阶段: 角色实现**
1. 实现ProductManager角色
2. 实现简单的PRD生成
3. 实现基础的文件保存

**第三阶段: 完整流程**
1. 添加Architect和Engineer角色
2. 实现完整的工作流
3. 添加ProjectRepo管理

### 7.2 简化版实现示例

```python
# simplified_metagpt.py

import asyncio
from typing import List, Optional
from openai import AsyncOpenAI

class SimpleLLM:
    """简化的LLM封装"""
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def ask(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

class SimpleAction:
    """简化的Action基类"""
    def __init__(self, llm: SimpleLLM):
        self.llm = llm
    
    async def run(self, context: str) -> str:
        raise NotImplementedError

class WritePRD(SimpleAction):
    """编写PRD"""
    async def run(self, context: str) -> str:
        prompt = f"""Based on the requirement: {context}
        
Write a detailed Product Requirements Document including:
1. Project Overview
2. Core Features
3. Technical Requirements
4. User Stories
"""
        return await self.llm.ask(prompt)

class WriteCode(SimpleAction):
    """编写代码"""
    async def run(self, context: str) -> str:
        prompt = f"""Based on the PRD: {context}
        
Write complete, production-ready code to implement the requirements.
Include all necessary files and proper structure.
"""
        return await self.llm.ask(prompt)

class SimpleRole:
    """简化的Role基类"""
    def __init__(self, name: str, actions: List[SimpleAction]):
        self.name = name
        self.actions = actions
    
    async def run(self, context: str) -> str:
        result = context
        for action in self.actions:
            result = await action.run(result)
        return result

async def simple_generate_repo(idea: str, api_key: str) -> dict:
    """简化版的generate_repo"""
    
    # 1. 初始化LLM
    llm = SimpleLLM(api_key=api_key)
    
    # 2. 创建角色
    pm = SimpleRole("ProductManager", [WritePRD(llm)])
    engineer = SimpleRole("Engineer", [WriteCode(llm)])
    
    # 3. 执行流程
    print("ProductManager: Writing PRD...")
    prd = await pm.run(idea)
    
    print("Engineer: Writing code...")
    code = await engineer.run(prd)
    
    # 4. 返回结果
    return {
        "prd": prd,
        "code": code
    }

# 使用示例
if __name__ == "__main__":
    result = asyncio.run(
        simple_generate_repo(
            idea="Create a 2048 game",
            api_key="your-api-key"
        )
    )
    print("PRD:", result["prd"])
    print("Code:", result["code"])
```

### 7.3 关键技术点

1. **异步编程**: 使用asyncio处理并发
2. **LLM调用**: 封装OpenAI API调用
3. **消息传递**: 实现角色间的通信机制
4. **文件管理**: 使用ProjectRepo管理输出
5. **成本控制**: 追踪token使用和成本

### 7.4 扩展方向

1. **支持更多LLM**: 添加Claude、Gemini等
2. **增强角色**: 添加QA、DevOps等角色
3. **工作流定制**: 支持自定义工作流
4. **增量开发**: 支持在现有项目基础上开发
5. **代码审查**: 添加自动化代码审查
6. **测试生成**: 自动生成单元测试

## 8. 总结

MetaGPT的核心优势:
1. **角色分工明确**: 模拟真实软件团队
2. **流程标准化**: 遵循软件工程最佳实践
3. **可扩展性强**: 易于添加新角色和动作
4. **成本可控**: 内置成本管理机制
5. **输出规范**: 生成完整的项目结构

复刻时的关键点:
1. 理解消息驱动的工作流
2. 实现清晰的角色-动作模型
3. 设计良好的prompt工程
4. 管理LLM调用成本
5. 保持代码的可维护性

通过本文档的分析,您应该能够理解MetaGPT的核心架构,并基于此实现一个类似的系统。建议从简化版开始,逐步添加功能,最终实现完整的多智能体协作系统。