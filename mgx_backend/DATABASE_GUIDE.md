# MGX Backend 数据库使用指南

## 📚 目录

1. [快速开始](#快速开始)
2. [数据库架构](#数据库架构)
3. [基本操作](#基本操作)
4. [集成到现有代码](#集成到现有代码)
5. [迁移到 PostgreSQL](#迁移到-postgresql)
6. [API 集成](#api-集成)

---

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /workspace/mgx_backend
pip install -r requirements.txt
```

### 2. 初始化数据库

```bash
python init_db.py
```

这将创建：
- SQLite 数据库文件 `mgx_backend.db`
- 所有必需的表
- 示例用户和项目数据

### 3. 验证安装

```python
from mgx_backend.database import get_db_manager

# 获取数据库管理器
db = get_db_manager()

# 查询用户
users = db.list_users()
print(f"Total users: {len(users)}")

# 查询项目
projects = db.list_projects()
print(f"Total projects: {len(projects)}")
```

---

## 🏗️ 数据库架构

### 表结构

```
┌─────────────────────────────────────────────────────┐
│                    users                            │
├─────────────────────────────────────────────────────┤
│ id (PK)                                             │
│ username (UNIQUE)                                   │
│ email (UNIQUE)                                      │
│ api_key_hash                                        │
│ created_at                                          │
│ updated_at                                          │
└─────────────────────────────────────────────────────┘
                    │
                    │ 1:N
                    ▼
┌─────────────────────────────────────────────────────┐
│                  projects                           │
├─────────────────────────────────────────────────────┤
│ id (PK)                                             │
│ user_id (FK → users.id)                             │
│ name                                                │
│ description                                         │
│ idea                                                │
│ status (pending/running/completed/failed)           │
│ project_path                                        │
│ investment                                          │
│ total_cost                                          │
│ metadata (JSON)                                     │
│ created_at                                          │
│ updated_at                                          │
│ completed_at                                        │
└─────────────────────────────────────────────────────┘
                    │
                    │ 1:N
                    ▼
┌─────────────────────────────────────────────────────┐
│                cost_records                         │
├─────────────────────────────────────────────────────┤
│ id (PK)                                             │
│ project_id (FK → projects.id)                       │
│ model                                               │
│ prompt_tokens                                       │
│ completion_tokens                                   │
│ total_cost                                          │
│ action_type                                         │
│ created_at                                          │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                  sessions                           │
├─────────────────────────────────────────────────────┤
│ id (PK)                                             │
│ user_id (FK → users.id)                             │
│ project_id (FK → projects.id)                       │
│ session_token (UNIQUE)                              │
│ status (active/expired/closed)                      │
│ metadata (JSON)                                     │
│ created_at                                          │
│ expires_at                                          │
└─────────────────────────────────────────────────────┘
```

---

## 📝 基本操作

### 用户管理

```python
from mgx_backend.database import get_db_manager, UserCreate

db = get_db_manager()

# 创建用户
user = db.create_user(UserCreate(
    username="john_doe",
    email="john@example.com",
    api_key="your_api_key_here"
))
print(f"Created user: {user.id}")

# 查询用户
user = db.get_user(user_id=1)
user = db.get_user_by_username("john_doe")

# 列出所有用户
users = db.list_users(skip=0, limit=10)
```

### 项目管理

```python
from mgx_backend.database import ProjectCreate

# 创建项目
project = db.create_project(
    ProjectCreate(
        name="My Calculator",
        description="A simple calculator app",
        idea="Create a calculator with +, -, *, / operations",
        investment=5.0
    ),
    user_id=1
)

# 更新项目状态
db.update_project_status(
    project_id=project.id,
    status="running",
    project_path="/workspace/projects/calculator"
)

# 更新项目成本
db.update_project_cost(project_id=project.id, total_cost=2.5)

# 查询项目
project = db.get_project(project_id=1)

# 列出用户的所有项目
projects = db.list_projects(user_id=1)
```

### 成本追踪

```python
from mgx_backend.database import CostRecordCreate

# 记录成本
cost = db.create_cost_record(CostRecordCreate(
    project_id=1,
    model="gpt-4-turbo",
    prompt_tokens=1000,
    completion_tokens=500,
    total_cost=0.025,
    action_type="WritePRD"
))

# 查询项目的所有成本记录
costs = db.get_project_costs(project_id=1)

# 获取项目总成本
total = db.get_total_cost(project_id=1)
print(f"Total cost: ${total:.4f}")
```

---

## 🔗 集成到现有代码

### 1. 修改 `software_company.py`

```python
from mgx_backend.database import get_db_manager, ProjectCreate

def generate_repo(
    idea: str,
    investment: float = 3.0,
    n_round: int = 5,
    project_name: str = "",
    project_path: str = "",
    user_id: int = 1  # 添加用户ID参数
) -> str:
    """Generate a complete software project from an idea."""
    
    # 获取数据库管理器
    db = get_db_manager()
    
    # 创建项目记录
    project = db.create_project(
        ProjectCreate(
            name=project_name or idea[:50],
            description=idea,
            idea=idea,
            investment=investment
        ),
        user_id=user_id
    )
    
    try:
        # 更新状态为运行中
        db.update_project_status(project.id, "running")
        
        # 原有的生成逻辑
        import asyncio
        from mgx_backend.config import Config
        from mgx_backend.context import Context
        from mgx_backend.team import Team
        
        config = Config()
        ctx = Context(config=config)
        team = Team(context=ctx)
        team.invest(investment)
        
        # 运行团队
        asyncio.run(team.run(n_round=n_round, idea=idea))
        
        # 更新项目状态和路径
        db.update_project_status(
            project.id,
            "completed",
            project_path=str(ctx.project_path)
        )
        
        # 更新成本
        db.update_project_cost(
            project.id,
            ctx.cost_manager.total_cost
        )
        
        return str(ctx.project_path)
        
    except Exception as e:
        # 更新状态为失败
        db.update_project_status(project.id, "failed")
        raise e
```

### 2. 修改 `cost_manager.py` 集成数据库

```python
from mgx_backend.database import get_db_manager, CostRecordCreate

class CostManager(BaseModel):
    """Track and manage API costs."""
    
    project_id: Optional[int] = None  # 添加项目ID
    
    def update(self, prompt_tokens: int, completion_tokens: int, model: str = 'gpt-4-turbo'):
        """Update cost based on token usage."""
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        
        pricing = self.PRICING.get(model, self.PRICING['gpt-4-turbo'])
        cost = (prompt_tokens * pricing['prompt'] + 
                completion_tokens * pricing['completion']) / 1000
        
        self.total_cost += cost
        
        # 记录到数据库
        if self.project_id:
            db = get_db_manager()
            db.create_cost_record(CostRecordCreate(
                project_id=self.project_id,
                model=model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_cost=cost
            ))
        
        if self.total_cost > self.max_budget:
            raise ValueError(f"Budget exceeded: ${self.total_cost:.2f} > ${self.max_budget:.2f}")
```

---

## 🐘 迁移到 PostgreSQL

### 1. 安装 PostgreSQL 驱动

```bash
pip install psycopg2-binary
```

### 2. 更新数据库 URL

```python
from mgx_backend.database import get_db_manager

# PostgreSQL
db = get_db_manager("postgresql://username:password@localhost/mgx_backend")

# 或者使用环境变量
import os
os.environ["DATABASE_URL"] = "postgresql://username:password@localhost/mgx_backend"
```

### 3. 创建 PostgreSQL 数据库

```bash
# 连接到 PostgreSQL
psql -U postgres

# 创建数据库
CREATE DATABASE mgx_backend;

# 创建用户
CREATE USER mgx_user WITH PASSWORD 'your_password';

# 授权
GRANT ALL PRIVILEGES ON DATABASE mgx_backend TO mgx_user;
```

### 4. 运行迁移

```python
from mgx_backend.database import get_db_manager

db = get_db_manager("postgresql://mgx_user:your_password@localhost/mgx_backend")
db.create_tables()
```

---

## 🌐 API 集成

### 更新 `api.py` 添加数据库端点

```python
from fastapi import FastAPI, HTTPException, Depends
from mgx_backend.database import (
    get_db_manager, DatabaseManager,
    UserCreate, UserResponse,
    ProjectCreate, ProjectResponse
)

app = FastAPI()

def get_db():
    """Dependency for database."""
    return get_db_manager()

@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: DatabaseManager = Depends(get_db)):
    """Create a new user."""
    return db.create_user(user)

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: DatabaseManager = Depends(get_db)):
    """Get user by ID."""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/projects/", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    user_id: int,
    db: DatabaseManager = Depends(get_db)
):
    """Create a new project."""
    return db.create_project(project, user_id)

@app.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: DatabaseManager = Depends(get_db)):
    """Get project by ID."""
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.get("/users/{user_id}/projects", response_model=list[ProjectResponse])
def list_user_projects(user_id: int, db: DatabaseManager = Depends(get_db)):
    """List all projects for a user."""
    return db.list_projects(user_id=user_id)
```

---

## 📊 查询示例

### SQLite 命令行

```bash
# 打开数据库
sqlite3 mgx_backend.db

# 查询所有用户
SELECT * FROM users;

# 查询所有项目
SELECT * FROM projects;

# 查询项目成本
SELECT p.name, SUM(c.total_cost) as total_cost
FROM projects p
LEFT JOIN cost_records c ON p.id = c.project_id
GROUP BY p.id;

# 查询用户的项目统计
SELECT u.username, COUNT(p.id) as project_count, SUM(p.total_cost) as total_spent
FROM users u
LEFT JOIN projects p ON u.id = p.user_id
GROUP BY u.id;
```

---

## 🔒 安全建议

1. **API Key 加密**：在生产环境中使用 bcrypt 或 argon2 加密 API key
2. **环境变量**：使用环境变量存储数据库凭据
3. **连接池**：在高并发场景下配置连接池
4. **备份**：定期备份数据库
5. **索引**：为常用查询字段添加索引

---

## 🎯 下一步

1. **添加认证**：集成 JWT 或 OAuth2
2. **添加缓存**：使用 Redis 缓存热数据
3. **添加监控**：使用 Prometheus + Grafana
4. **添加日志**：使用 ELK Stack
5. **添加测试**：编写单元测试和集成测试

---

## 📞 需要帮助？

如果您有任何问题或需要进一步的帮助，请告诉我！