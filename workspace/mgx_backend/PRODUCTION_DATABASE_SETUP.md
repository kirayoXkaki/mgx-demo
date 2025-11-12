# 🚀 生产环境数据库配置指南

## 📊 数据库选择建议

### 推荐：PostgreSQL（首选）⭐

**为什么选择 PostgreSQL：**
- ✅ **功能强大**：支持 JSON、全文搜索、数组等高级特性
- ✅ **性能优秀**：并发处理能力强，适合生产环境
- ✅ **开源免费**：社区活跃，文档完善
- ✅ **SQLAlchemy 完美支持**：你的项目已经使用 SQLAlchemy，迁移简单
- ✅ **云服务支持好**：AWS RDS、Google Cloud SQL、阿里云 RDS 都有托管服务
- ✅ **数据完整性**：ACID 事务支持，数据安全可靠

### 备选方案

1. **MySQL/MariaDB**
   - 适合：已有 MySQL 基础设施
   - 优点：使用广泛，社区大
   - 缺点：功能相对 PostgreSQL 较少

2. **云数据库服务**
   - **AWS RDS PostgreSQL**：适合部署在 AWS
   - **Google Cloud SQL**：适合部署在 GCP
   - **阿里云 RDS PostgreSQL**：适合国内部署
   - **Supabase**：开源 Firebase 替代，提供 PostgreSQL + 实时功能

---

## 🛠️ 本地 PostgreSQL 安装和配置

### macOS (使用 Homebrew)

```bash
# 安装 PostgreSQL
brew install postgresql@15

# 启动服务
brew services start postgresql@15

# 创建数据库和用户
psql postgres

# 在 psql 中执行：
CREATE DATABASE mgx_backend;
CREATE USER mgx_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE mgx_backend TO mgx_user;
\q
```

### Linux (Ubuntu/Debian)

```bash
# 安装 PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# 切换到 postgres 用户
sudo -u postgres psql

# 创建数据库和用户
CREATE DATABASE mgx_backend;
CREATE USER mgx_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE mgx_backend TO mgx_user;
\q
```

### Windows

1. 下载 PostgreSQL：https://www.postgresql.org/download/windows/
2. 运行安装程序，记住设置的密码
3. 使用 pgAdmin 或命令行创建数据库

---

## 📦 安装 Python 驱动

```bash
cd workspace/mgx_backend
pip install psycopg2-binary  # PostgreSQL 驱动
# 或者使用异步版本（如果使用 async SQLAlchemy）
# pip install asyncpg
```

更新 `requirements.txt`：

```txt
# Database
sqlalchemy>=2.0.0
alembic>=1.12.0
psycopg2-binary>=2.9.0  # PostgreSQL 驱动
```

---

## ⚙️ 环境变量配置

### 创建 `.env` 文件

在 `workspace/mgx_backend/` 目录下创建 `.env`：

```bash
# 数据库配置
DATABASE_URL=postgresql://mgx_user:your_secure_password@localhost:5432/mgx_backend

# 或者使用连接池（推荐生产环境）
# DATABASE_URL=postgresql://mgx_user:your_secure_password@localhost:5432/mgx_backend?pool_size=10&max_overflow=20
```

### 更新 `database.py` 支持环境变量

```python
import os
from typing import Optional

def get_db_manager(database_url: Optional[str] = None) -> DatabaseManager:
    """Get or create database manager instance."""
    global db_manager
    
    # 优先使用环境变量
    if database_url is None:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./mgx_backend.db")
    
    if db_manager is None:
        db_manager = DatabaseManager(database_url)
        db_manager.create_tables()
    return db_manager
```

---

## 🔄 数据迁移方案

### 方案 1：使用 Alembic（推荐）

Alembic 是 SQLAlchemy 的数据库迁移工具，适合生产环境。

#### 1. 初始化 Alembic

```bash
cd workspace/mgx_backend
alembic init alembic
```

#### 2. 配置 `alembic/env.py`

```python
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import Base
from database import UserModel, ProjectModel, CostRecordModel, SessionModel

# 从环境变量读取数据库 URL
config = context.config
database_url = os.getenv("DATABASE_URL", "sqlite:///./mgx_backend.db")
config.set_main_option("sqlalchemy.url", database_url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

#### 3. 创建初始迁移

```bash
# 自动生成迁移文件
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

### 方案 2：从 SQLite 迁移数据（如果已有数据）

```python
# migrate_from_sqlite.py
from mgx_backend.database import get_db_manager, UserModel, ProjectModel, CostRecordModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def migrate_data():
    """从 SQLite 迁移数据到 PostgreSQL"""
    
    # 连接 SQLite（源数据库）
    sqlite_engine = create_engine("sqlite:///./mgx_backend.db")
    SqliteSession = sessionmaker(bind=sqlite_engine)
    sqlite_session = SqliteSession()
    
    # 连接 PostgreSQL（目标数据库）
    postgres_url = os.getenv("DATABASE_URL")
    postgres_db = get_db_manager(postgres_url)
    postgres_session = postgres_db.get_session()
    
    try:
        # 迁移用户
        users = sqlite_session.query(UserModel).all()
        for user in users:
            existing = postgres_session.query(UserModel).filter(
                UserModel.username == user.username
            ).first()
            if not existing:
                postgres_session.add(UserModel(
                    username=user.username,
                    email=user.email,
                    api_key_hash=user.api_key_hash,
                    created_at=user.created_at,
                    updated_at=user.updated_at
                ))
        
        postgres_session.commit()
        print("✅ Users migrated")
        
        # 迁移项目
        projects = sqlite_session.query(ProjectModel).all()
        for project in projects:
            # 需要先找到对应的用户
            user = postgres_session.query(UserModel).filter(
                UserModel.username == project.user.username
            ).first()
            if user:
                existing = postgres_session.query(ProjectModel).filter(
                    ProjectModel.name == project.name,
                    ProjectModel.user_id == user.id
                ).first()
                if not existing:
                    postgres_session.add(ProjectModel(
                        user_id=user.id,
                        name=project.name,
                        description=project.description,
                        idea=project.idea,
                        status=project.status,
                        project_path=project.project_path,
                        investment=project.investment,
                        total_cost=project.total_cost,
                        extra_data=project.extra_data,
                        created_at=project.created_at,
                        updated_at=project.updated_at,
                        completed_at=project.completed_at
                    ))
        
        postgres_session.commit()
        print("✅ Projects migrated")
        
        # 迁移成本记录
        cost_records = sqlite_session.query(CostRecordModel).all()
        for record in cost_records:
            # 找到对应的项目
            project = postgres_session.query(ProjectModel).filter(
                ProjectModel.name == record.project.name
            ).first()
            if project:
                postgres_session.add(CostRecordModel(
                    project_id=project.id,
                    model=record.model,
                    prompt_tokens=record.prompt_tokens,
                    completion_tokens=record.completion_tokens,
                    total_cost=record.total_cost,
                    action_type=record.action_type,
                    created_at=record.created_at
                ))
        
        postgres_session.commit()
        print("✅ Cost records migrated")
        
        print("\n🎉 Migration completed!")
        
    except Exception as e:
        postgres_session.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        sqlite_session.close()
        postgres_session.close()

if __name__ == "__main__":
    import os
    os.environ["DATABASE_URL"] = "postgresql://mgx_user:password@localhost:5432/mgx_backend"
    migrate_data()
```

---

## ☁️ 云数据库服务配置

### AWS RDS PostgreSQL

1. **创建 RDS 实例**
   - 登录 AWS Console
   - 选择 RDS → Create database
   - 选择 PostgreSQL
   - 配置实例规格、存储、安全组

2. **获取连接信息**
   ```bash
   # 连接字符串格式
   DATABASE_URL=postgresql://username:password@your-rds-endpoint.region.rds.amazonaws.com:5432/mgx_backend
   ```

### 阿里云 RDS PostgreSQL

1. **创建 RDS 实例**
   - 登录阿里云控制台
   - 选择 RDS → 创建实例
   - 选择 PostgreSQL 引擎

2. **配置白名单和安全组**
   - 添加应用服务器 IP 到白名单

3. **连接字符串**
   ```bash
   DATABASE_URL=postgresql://username:password@your-rds-endpoint.mysql.rds.aliyuncs.com:5432/mgx_backend
   ```

### Supabase（推荐用于快速上线）

1. **注册账号**：https://supabase.com
2. **创建项目**
3. **获取连接字符串**
   ```bash
   DATABASE_URL=postgresql://postgres:password@db.xxx.supabase.co:5432/postgres
   ```

---

## 🔒 生产环境安全建议

### 1. 使用连接池

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    database_url,
    poolclass=QueuePool,
    pool_size=10,          # 连接池大小
    max_overflow=20,      # 最大溢出连接数
    pool_pre_ping=True,    # 连接前检查连接是否有效
    pool_recycle=3600     # 1小时后回收连接
)
```

### 2. 使用环境变量管理敏感信息

```bash
# 使用 .env 文件（不要提交到 Git）
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

### 3. 启用 SSL 连接（云数据库）

```python
DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require
```

### 4. 定期备份

```bash
# 使用 pg_dump 备份
pg_dump -h localhost -U mgx_user -d mgx_backend > backup_$(date +%Y%m%d).sql

# 恢复
psql -h localhost -U mgx_user -d mgx_backend < backup_20240101.sql
```

---

## 📝 更新 API 代码

### 在 `api.py` 中初始化数据库

```python
import os
from mgx_backend.database import get_db_manager

# 在应用启动时初始化数据库
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    database_url = os.getenv("DATABASE_URL", "sqlite:///./mgx_backend.db")
    db = get_db_manager(database_url)
    print(f"✅ Database initialized: {database_url.split('@')[-1] if '@' in database_url else database_url}")
```

---

## ✅ 验证配置

### 测试数据库连接

```python
# test_db_connection.py
import os
from mgx_backend.database import get_db_manager

os.environ["DATABASE_URL"] = "postgresql://mgx_user:password@localhost:5432/mgx_backend"

db = get_db_manager()
users = db.list_users()
print(f"✅ Database connected! Found {len(users)} users")
```

---

## 🚀 快速开始清单

- [ ] 安装 PostgreSQL（本地或使用云服务）
- [ ] 创建数据库和用户
- [ ] 安装 `psycopg2-binary`
- [ ] 配置 `DATABASE_URL` 环境变量
- [ ] 更新 `database.py` 支持环境变量
- [ ] 运行迁移或初始化数据库
- [ ] 测试连接
- [ ] 配置备份策略
- [ ] 更新部署脚本

---

## 📚 参考资源

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)
- [Alembic 文档](https://alembic.sqlalchemy.org/)
- [Supabase 文档](https://supabase.com/docs)

