"""Database models and management."""

import os
from datetime import datetime
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import QueuePool
from pydantic import BaseModel

Base = declarative_base()


# SQLAlchemy Models
class UserModel(Base):
    """User table."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    api_key_hash = Column(String(255))  # Hashed API key
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = relationship("ProjectModel", back_populates="user")
    sessions = relationship("SessionModel", back_populates="user")


class ProjectModel(Base):
    """Project table."""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    idea = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    project_path = Column(String(500))
    investment = Column(Float, default=3.0)
    total_cost = Column(Float, default=0.0)
    extra_data = Column(JSON)  # Changed from 'metadata' to 'extra_data' to avoid SQLAlchemy reserved word
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("UserModel", back_populates="projects")
    sessions = relationship("SessionModel", back_populates="project")
    costs = relationship("CostRecordModel", back_populates="project")


class SessionModel(Base):
    """Session table for tracking user sessions."""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"))
    session_token = Column(String(255), unique=True, index=True)
    status = Column(String(20), default="active")  # active, expired, closed
    extra_data = Column(JSON)  # Changed from 'metadata' to 'extra_data'
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    # Relationships
    user = relationship("UserModel", back_populates="sessions")
    project = relationship("ProjectModel", back_populates="sessions")


class CostRecordModel(Base):
    """Cost tracking table."""
    __tablename__ = "cost_records"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    model = Column(String(50), nullable=False)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    action_type = Column(String(50))  # WritePRD, WriteDesign, WriteCode
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("ProjectModel", back_populates="costs")


# Pydantic Schemas for API
class UserCreate(BaseModel):
    username: str
    email: str
    api_key: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    idea: str
    investment: float = 3.0


class ProjectResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    idea: str
    status: str
    project_path: Optional[str]
    investment: float
    total_cost: float
    created_at: datetime
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CostRecordCreate(BaseModel):
    project_id: int
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_cost: float
    action_type: Optional[str] = None


class CostRecordResponse(BaseModel):
    id: int
    project_id: int
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_cost: float
    action_type: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Database Manager
class DatabaseManager:
    """Manage database connections and operations."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize database manager.
        
        Args:
            database_url: Database connection URL (defaults to DATABASE_URL env var or SQLite)
                - SQLite: "sqlite:///./mgx_backend.db"
                - PostgreSQL: "postgresql://user:password@localhost/dbname"
                - MySQL: "mysql://user:password@localhost/dbname"
        """
        if database_url is None:
            database_url = os.getenv("DATABASE_URL", "sqlite:///./mgx_backend.db")
        
        # Configure connection pool for production databases
        if database_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
            poolclass = None
            pool_kwargs = {}
        else:
            # PostgreSQL/MySQL connection pool settings
            connect_args = {}
            poolclass = QueuePool
            pool_kwargs = {
                "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
                "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
                "pool_pre_ping": True,  # Verify connections before using
                "pool_recycle": 3600,   # Recycle connections after 1 hour
            }
        
        self.engine = create_engine(
            database_url,
            connect_args=connect_args,
            poolclass=poolclass,
            **pool_kwargs
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables."""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """Get database session."""
        return self.SessionLocal()
    
    # User operations
    def create_user(self, user: UserCreate) -> UserModel:
        """Create a new user."""
        db = self.get_session()
        try:
            db_user = UserModel(
                username=user.username,
                email=user.email,
                api_key_hash=user.api_key  # Should be hashed in production
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        finally:
            db.close()
    
    def get_user(self, user_id: int) -> Optional[UserModel]:
        """Get user by ID."""
        db = self.get_session()
        try:
            return db.query(UserModel).filter(UserModel.id == user_id).first()
        finally:
            db.close()
    
    def get_user_by_username(self, username: str) -> Optional[UserModel]:
        """Get user by username."""
        db = self.get_session()
        try:
            return db.query(UserModel).filter(UserModel.username == username).first()
        finally:
            db.close()
    
    def list_users(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        """List all users."""
        db = self.get_session()
        try:
            return db.query(UserModel).offset(skip).limit(limit).all()
        finally:
            db.close()
    
    # Project operations
    def create_project(self, project: ProjectCreate, user_id: int) -> ProjectModel:
        """Create a new project."""
        db = self.get_session()
        try:
            db_project = ProjectModel(
                user_id=user_id,
                name=project.name,
                description=project.description,
                idea=project.idea,
                investment=project.investment
            )
            db.add(db_project)
            db.commit()
            db.refresh(db_project)
            return db_project
        finally:
            db.close()
    
    def get_project(self, project_id: int) -> Optional[ProjectModel]:
        """Get project by ID."""
        db = self.get_session()
        try:
            return db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        finally:
            db.close()
    
    def update_project_status(self, project_id: int, status: str, project_path: Optional[str] = None):
        """Update project status."""
        db = self.get_session()
        try:
            project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
            if project:
                project.status = status
                if project_path:
                    project.project_path = project_path
                if status == "completed":
                    project.completed_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    
    def update_project_cost(self, project_id: int, total_cost: float):
        """Update project total cost."""
        db = self.get_session()
        try:
            project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
            if project:
                project.total_cost = total_cost
                db.commit()
        finally:
            db.close()
    
    def list_projects(self, user_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[ProjectModel]:
        """List projects, optionally filtered by user."""
        db = self.get_session()
        try:
            query = db.query(ProjectModel)
            if user_id:
                query = query.filter(ProjectModel.user_id == user_id)
            return query.offset(skip).limit(limit).all()
        finally:
            db.close()
    
    # Cost record operations
    def create_cost_record(self, cost: CostRecordCreate) -> CostRecordModel:
        """Create a cost record."""
        db = self.get_session()
        try:
            db_cost = CostRecordModel(**cost.dict())
            db.add(db_cost)
            db.commit()
            db.refresh(db_cost)
            return db_cost
        finally:
            db.close()
    
    def get_project_costs(self, project_id: int) -> List[CostRecordModel]:
        """Get all cost records for a project."""
        db = self.get_session()
        try:
            return db.query(CostRecordModel).filter(CostRecordModel.project_id == project_id).all()
        finally:
            db.close()
    
    def get_total_cost(self, project_id: int) -> float:
        """Get total cost for a project."""
        db = self.get_session()
        try:
            result = db.query(CostRecordModel).filter(
                CostRecordModel.project_id == project_id
            ).with_entities(CostRecordModel.total_cost).all()
            return sum(r[0] for r in result)
        finally:
            db.close()


# Global database instance
db_manager: Optional[DatabaseManager] = None


def get_db_manager(database_url: Optional[str] = None) -> DatabaseManager:
    """Get or create database manager instance.
    
    Args:
        database_url: Optional database URL. If not provided, uses DATABASE_URL 
                     environment variable or defaults to SQLite.
    
    Returns:
        DatabaseManager instance
    """
    global db_manager
    
    # Use provided URL or environment variable
    if database_url is None:
        database_url = os.getenv("DATABASE_URL", "sqlite:///./mgx_backend.db")
    
    # Create new instance if doesn't exist
    # Note: We don't check URL change to avoid connection issues
    # If you need to change database, restart the application
    if db_manager is None:
        db_manager = DatabaseManager(database_url)
        db_manager.create_tables()
    
    return db_manager