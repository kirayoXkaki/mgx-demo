"""FastAPI backend wrapper for MGX Backend."""

import asyncio
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import shutil
import json
import subprocess
import base64

from mgx_backend.software_company import generate_repo
from mgx_backend.config import Config
from mgx_backend.context import Context
from mgx_backend.team import Team
from mgx_backend.roles import ProductManager, Architect, Engineer
from mgx_backend.project_repo import ProjectRepo
from mgx_backend.database import (
    get_db_manager, UserRegister, UserLogin, UserUpdate, UserResponse,
    ConversationCreate, ConversationUpdate, ConversationResponse, UserModel, TaskModel
)
from mgx_backend.auth import (
    get_password_hash, verify_password, create_access_token,
    authenticate_user, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from datetime import timedelta


app = FastAPI(title="MGX Backend API", version="1.0.0")


@app.get("/api/health")
async def health_check():
    """Health check endpoint for deployment monitoring."""
    return {"status": "healthy", "service": "MGX Backend API"}

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# WebSocket connections (must stay in memory, cannot be serialized)
websocket_connections: Dict[str, WebSocket] = {}
# Message queue for messages sent before WebSocket connection is established (temporary, can stay in memory)
pending_messages: Dict[str, list] = {}


class GenerateRequest(BaseModel):
    idea: str
    investment: float = 5.0
    n_round: int = 5


class GitHubUploadRequest(BaseModel):
    task_id: str
    repo_name: str
    description: str = ""
    is_private: bool = False
    github_token: str


class TaskStatus(BaseModel):
    task_id: str
    status: str  # pending, running, completed, failed
    progress: int  # 0-100
    current_stage: str
    cost: float
    result: Optional[dict] = None
    error: Optional[str] = None
    created_at: str
    updated_at: str


def get_task_dict(task_id: str) -> dict:
    """Get task as dictionary from database."""
    db = get_db_manager()
    task = db.get_task(task_id)
    if not task:
        return None
    return {
        "task_id": task.task_id,
        "status": task.status,
        "progress": task.progress,
        "current_stage": task.current_stage,
        "cost": task.cost,
        "idea": task.idea,
        "investment": task.investment,
        "n_round": task.n_round,
        "result": task.result,
        "error": task.error,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None
    }

async def send_progress(task_id: str, data: dict):
    """Send progress update via WebSocket and update database."""
    # Update task in database if status/progress/cost changed
    db = get_db_manager()
    update_data = {}
    if "status" in data:
        update_data["status"] = data["status"]
    if "progress" in data:
        update_data["progress"] = data["progress"]
    if "cost" in data:
        update_data["cost"] = data["cost"]
    if "stage" in data:
        update_data["current_stage"] = data["stage"]
    if "error" in data:
        update_data["error"] = data["error"]
    if "result" in data:
        update_data["result"] = data["result"]
    
    if update_data:
        db.update_task(task_id, **update_data)
    
    # Send via WebSocket
    if task_id in websocket_connections:
        try:
            await websocket_connections[task_id].send_json(data)
        except:
            pass
    else:
        # WebSocket not yet connected, queue the message
        if task_id not in pending_messages:
            pending_messages[task_id] = []
        pending_messages[task_id].append(data)
        print(f"📬 [API] WebSocket not connected for {task_id}, queued message. Queue size: {len(pending_messages[task_id])}")


async def run_generation_task(task_id: str, idea: str, investment: float, n_round: int):
    """Run the generation task in background."""
    db = get_db_manager()
    try:
        db.update_task(task_id, status="running", current_stage="Initializing")
        
        await send_progress(task_id, {
            "type": "status",
            "status": "running",
            "stage": "Initializing",
            "progress": 10,
            "cost": 0.0
        })
        
        # Create custom context to track progress
        config = Config.default()
        config.update_project(project_name=f"project_{task_id}")
        ctx = Context(config=config)
        
        team = Team(context=ctx)
        team.hire([ProductManager(), Architect(), Engineer()])
        team.invest(investment)
        
        await send_progress(task_id, {
            "type": "status",
            "stage": "ProductManager working",
            "progress": 20,
            "cost": ctx.cost_manager.total_cost
        })
        
        # Progress callback for real-time updates
        async def progress_callback(update: dict):
            """Callback for progress updates from team execution."""
            update_type = update.get("type", "progress")
            role = update.get("role", "")
            action = update.get("action", "")
            stage = update.get("stage", "")
            message = update.get("message", "")
            
            # Debug: Log chat_message type updates
            if update_type == "chat_message":
                print(f"💬 [API] Received chat_message: role={role}, message={message[:50] if message else 'None'}...")
            
            # Calculate progress based on role and action
            base_progress = 20
            if role == "ProductManager":
                if update_type == "thinking":
                    progress = 25
                elif update_type == "action_start" and action == "WritePRD":
                    progress = 30
                elif update_type == "action_executing":
                    progress = 35
                elif update_type == "action_complete":
                    progress = 40
                else:
                    progress = 30
            elif role == "Architect":
                if update_type == "thinking":
                    progress = 50
                elif update_type == "action_start" and action == "WriteDesign":
                    progress = 55
                elif update_type == "action_executing":
                    progress = 60
                elif update_type == "action_complete":
                    progress = 65
                else:
                    progress = 55
            elif role == "Engineer":
                if update_type == "thinking":
                    progress = 70
                elif update_type == "action_start" and action == "WriteCode":
                    progress = 75
                elif update_type == "action_executing":
                    progress = 80
                elif update_type == "action_complete":
                    progress = 85
                else:
                    progress = 75
            else:
                task_dict = get_task_dict(task_id)
                progress = task_dict.get("progress", 20) if task_dict else 20
            
            # Progress updated via send_progress
            
            # Update cost in real-time from context
            current_cost = ctx.cost_manager.total_cost
            # Cost updated via send_progress
            
            # Include additional fields for chat and file updates
            progress_data = {
                "type": update_type,
                "role": role,
                "action": action,
                "stage": stage,
                "progress": progress,
                "cost": current_cost,  # Include cost in progress updates
                "message": message
            }
            
            # Add stream chunk data
            if update_type == "stream_chunk":
                progress_data["chunk"] = update.get("chunk", "")
                progress_data["accumulated"] = update.get("accumulated", "")
            
            # Add file update data
            if update_type in ["file_update", "file_content", "file_complete"]:
                progress_data["filepath"] = update.get("filepath", "")
                if update_type in ["file_content", "file_complete"]:
                    progress_data["content"] = update.get("content", "")
                if update_type == "file_update":
                    progress_data["file_action"] = update.get("action", "creating")
            
            await send_progress(task_id, progress_data)
        
        # Run the team with progress callback
        await send_progress(task_id, {
            "type": "status",
            "stage": "Starting team collaboration...",
            "progress": 20,
            "cost": ctx.cost_manager.total_cost
        })
        history = await team.run(n_round=n_round, idea=idea, progress_callback=progress_callback)
        
        # Track final progress through completed messages
        for i, msg in enumerate(history):
            if msg.cause_by == "WritePRD":
                stage = "ProductManager: PRD completed ✓"
            elif msg.cause_by == "WriteDesign":
                stage = "Architect: System design completed ✓"
            elif msg.cause_by == "WriteCode":
                stage = "Engineer: Code implementation completed ✓"
            else:
                stage = f"{msg.role}: Completed"
            
            progress = 20 + int((i / len(history)) * 60)
            await send_progress(task_id, {
                "type": "status",
                "stage": stage,
                "progress": min(progress, 90),
                "cost": ctx.cost_manager.total_cost
            })
        
        # Save outputs
        await send_progress(task_id, {
            "type": "status",
            "stage": "Saving project files...",
            "progress": 90,
            "cost": ctx.cost_manager.total_cost
        })
        await send_progress(task_id, {
            "type": "saving",
            "stage": "Saving project files...",
            "progress": 90,
            "cost": ctx.cost_manager.total_cost,
            "message": "Saving generated files to project directory"
        })
        
        repo = ProjectRepo(ctx.project_path)
        print(f"📁 Saving outputs to: {ctx.project_path}")
        
        for message in history:
            try:
                if message.cause_by == "WritePRD":
                    print("💾 Saving PRD...")
                    await repo.save_prd(message.content)
                    print("✅ PRD saved")
                elif message.cause_by == "WriteDesign":
                    print("💾 Saving Design...")
                    await repo.save_design(message.content)
                    print("✅ Design saved")
                elif message.cause_by == "WriteCode":
                    print("💾 Saving Code...")
                    print(f"   Code content length: {len(message.content)}")
                    print(f"   First 500 chars: {message.content[:500]}")
                    await repo.save_code_files(message.content)
                    print("✅ Code saved")
                    # List saved files
                    print(f"   Saved files: {repo.srcs.all_files}")
                    
                    # Read all saved code files and send to frontend via WebSocket
                    print("📤 Sending saved code files to frontend...")
                    for filepath in repo.srcs.all_files:
                        try:
                            content = await repo.srcs.read(filepath)
                            if content:
                                # Get current task status
                                task_dict = get_task_dict(task_id)
                                current_progress = task_dict.get("progress", 90) if task_dict else 90
                                current_stage = task_dict.get("current_stage", "Saving project files...") if task_dict else "Saving project files..."
                                
                                # Send file_update event
                                await send_progress(task_id, {
                                    "type": "file_update",
                                    "filepath": f"src/{filepath}",
                                    "file_action": "creating",
                                    "progress": current_progress,
                                    "stage": current_stage,
                                    "cost": ctx.cost_manager.total_cost,
                                    "message": f"Created file: src/{filepath}"
                                })
                                
                                # Send file_content event
                                await send_progress(task_id, {
                                    "type": "file_content",
                                    "filepath": f"src/{filepath}",
                                    "content": content,
                                    "progress": current_progress,
                                    "stage": current_stage,
                                    "cost": ctx.cost_manager.total_cost,
                                    "message": f"File content: src/{filepath}"
                                })
                                
                                # Send file_complete event
                                await send_progress(task_id, {
                                    "type": "file_complete",
                                    "filepath": f"src/{filepath}",
                                    "content": content,
                                    "progress": current_progress,
                                    "stage": current_stage,
                                    "cost": ctx.cost_manager.total_cost,
                                    "message": f"File complete: src/{filepath}"
                                })
                                print(f"   ✅ Sent: src/{filepath} ({len(content)} chars)")
                        except Exception as e:
                            print(f"   ❌ Error sending file {filepath}: {e}")
                    
                    # Also check root files
                    from pathlib import Path
                    project_root = Path(ctx.project_path)
                    root_files = [str(f.relative_to(project_root)) for f in project_root.rglob("*") if f.is_file() and not str(f.relative_to(project_root)).startswith(('src/', 'docs/'))]
                    if root_files:
                        print(f"   Root files: {root_files}")
            except Exception as e:
                print(f"❌ Error saving {message.cause_by}: {e}")
                import traceback
                traceback.print_exc()
                raise
        
        result = {
            "project_path": str(ctx.project_path),
            "files": repo.srcs.all_files,
            "docs": repo.docs.all_files,
            "cost": ctx.cost_manager.total_cost,
            "tokens": ctx.cost_manager.total_tokens
        }
        db.update_task(
            task_id,
            status="completed",
            progress=100,
            current_stage="Completed",
            cost=ctx.cost_manager.total_cost,
            result=result
        )
        
        # Save project to database for persistence
        try:
            db = get_db_manager()
            from mgx_backend.database import ProjectCreate
            
            # Get task to find user_id if available
            task_dict = get_task_dict(task_id)
            user_id = None
            
            # Try to get user_id from task's result or extra_data
            if task_dict:
                if task_dict.get("result") and isinstance(task_dict["result"], dict):
                    user_id = task_dict["result"].get("user_id")
                # Also check if task has extra_data with user_id
                if not user_id and task_dict.get("extra_data"):
                    if isinstance(task_dict["extra_data"], dict):
                        user_id = task_dict["extra_data"].get("user_id")
            
            # If no user_id in task, try to find from conversations that reference this task_id
            if not user_id:
                from mgx_backend.database import ConversationHistoryModel, get_db
                db_session = next(get_db())
                try:
                    # Find conversation with this task_id in extra_data
                    all_conversations = db_session.query(ConversationHistoryModel).all()
                    for conv in all_conversations:
                        if conv.extra_data and isinstance(conv.extra_data, dict):
                            if conv.extra_data.get("task_id") == task_id:
                                user_id = conv.user_id
                                print(f"📁 [API] Found user_id from conversation: {user_id}")
                                break
                finally:
                    db_session.close()
            
            # If still no user_id, try to find a default user (first user in database)
            if not user_id:
                users = db.list_users(limit=1)
                if users:
                    user_id = users[0].id
                    print(f"⚠️ [API] No user_id found, using default user: {user_id}")
                else:
                    print(f"⚠️ [API] No users found in database, cannot create project")
                    user_id = None
            
            if user_id:
                project_name = f"Project {task_id[:8]}"
                project_description = idea[:200] if idea else f"Generated project {task_id[:8]}"
                
                print(f"💾 [API] Creating project in database: {project_name}, path: {ctx.project_path}, user_id: {user_id}")
                
                # Create project
                project = db.create_project(
                    ProjectCreate(
                        name=project_name,
                        description=project_description,
                        idea=idea,
                        investment=investment
                    ),
                    user_id=user_id
                )
                
                # Update project status and path
                db.update_project_status(
                    project.id,
                    "completed",
                    project_path=str(ctx.project_path)
                )
                
                # Update project cost
                db.update_project_cost(
                    project.id,
                    ctx.cost_manager.total_cost
                )
                
                # Store project_id and task_id in extra_data for easy lookup
                from mgx_backend.database import ProjectModel, get_db
                db_session = next(get_db())
                try:
                    db_project = db_session.query(ProjectModel).filter(ProjectModel.id == project.id).first()
                    if db_project:
                        extra_data = db_project.extra_data or {}
                        extra_data["task_id"] = task_id
                        db_project.extra_data = extra_data
                        db_session.commit()
                        print(f"✅ [API] Project saved successfully: project_id={project.id}, task_id={task_id}")
                finally:
                    db_session.close()
            else:
                print(f"⚠️ [API] Cannot create project: no user_id available")
            
        except Exception as e:
            print(f"⚠️ [API] Failed to save project to database: {e}")
            import traceback
            traceback.print_exc()
        
        task_dict = get_task_dict(task_id)
        await send_progress(task_id, {
            "type": "complete",
            "status": "completed",
            "progress": 100,
            "cost": task_dict["cost"] if task_dict else ctx.cost_manager.total_cost,
            "result": result
        })
        
    except Exception as e:
        db.update_task(task_id, status="failed", error=str(e))
        
        await send_progress(task_id, {
            "type": "error",
            "status": "failed",
            "error": str(e)
        })


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "MGX Backend API",
        "version": "1.0.0",
        "status": "running"
    }


@app.post("/api/generate")
async def generate(request: GenerateRequest, background_tasks: BackgroundTasks):
    """Start a new generation task."""
    task_id = str(uuid.uuid4())
    
    # Create task in database
    db = get_db_manager()
    db.create_task(task_id, request.idea, request.investment, request.n_round)
    
    # Start background task
    background_tasks.add_task(
        run_generation_task,
        task_id,
        request.idea,
        request.investment,
        request.n_round
    )
    
    return {"task_id": task_id, "status": "pending"}


@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    """Get task status."""
    task_dict = get_task_dict(task_id)
    if not task_dict:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_dict


@app.websocket("/api/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    websocket_connections[task_id] = websocket
    
    try:
        # Send initial status (format matches frontend expectations)
        task_dict = get_task_dict(task_id)
        if task_dict:
            await websocket.send_json({
                "type": "status",
                "status": task_dict.get("status", "pending"),
                "progress": task_dict.get("progress", 0),
                "stage": task_dict.get("current_stage", "Queued"),
                "cost": task_dict.get("cost", 0.0),
                "result": task_dict.get("result"),
                "error": task_dict.get("error")
            })
        
        # Send any pending messages that were queued before connection
        if task_id in pending_messages:
            print(f"📬 [API] WebSocket connected for {task_id}, sending {len(pending_messages[task_id])} pending messages")
            for pending_msg in pending_messages[task_id]:
                try:
                    await websocket.send_json(pending_msg)
                except:
                    pass
            # Clear the queue after sending
            del pending_messages[task_id]
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        if task_id in websocket_connections:
            del websocket_connections[task_id]
        if task_id in pending_messages:
            del pending_messages[task_id]


@app.get("/api/files/{task_id}")
async def get_files(task_id: str):
    """Get list of generated files."""
    project_path = None
    
    # Get task from database
    task_dict = get_task_dict(task_id)
    if task_dict:
        if task_dict["status"] != "completed":
            raise HTTPException(status_code=400, detail="Task not completed")
        if task_dict.get("result") and task_dict["result"].get("project_path"):
            project_path = task_dict["result"]["project_path"]
    
    if not project_path:
        # Try to get from database by project_id (if task_id is numeric)
        try:
            project_id = int(task_id)
            db = get_db_manager()
            project = db.get_project(project_id)
            if project and project.project_path:
                project_path = project.project_path
                print(f"📁 [API] Found project_path from database by project_id: {project_path}")
            else:
                # If project exists but no project_path, return empty files instead of 404
                if project:
                    print(f"⚠️ [API] Project {project_id} exists but has no project_path, returning empty files")
                    return {"files": []}
                raise HTTPException(status_code=404, detail="Project not found or no project_path")
        except (ValueError, TypeError):
            # task_id is not numeric (UUID), try to find project by searching conversations
            # First try to find conversation with this task_id in extra_data
            db = get_db_manager()
            try:
                # Search all conversations for this task_id in extra_data
                from mgx_backend.database import ConversationHistoryModel, get_db
                
                db_session = next(get_db())
                try:
                    # Query all conversations and check extra_data manually (SQLite JSON support is limited)
                    all_conversations = db_session.query(ConversationHistoryModel).all()
                    matching_conversation = None
                    for conv in all_conversations:
                        if conv.extra_data and isinstance(conv.extra_data, dict):
                            if conv.extra_data.get("task_id") == task_id:
                                matching_conversation = conv
                                break
                    
                    if matching_conversation:
                        # Get project_id from the matching conversation
                        if matching_conversation.project_id:
                            project = db.get_project(matching_conversation.project_id)
                            if project and project.project_path:
                                project_path = project.project_path
                                print(f"📁 [API] Found project_path from conversation extra_data: {project_path}")
                            elif project:
                                print(f"⚠️ [API] Project {matching_conversation.project_id} exists but has no project_path")
                        else:
                            print(f"⚠️ [API] Conversation found but no project_id, task_id: {task_id}")
                finally:
                    db_session.close()
            except Exception as e:
                print(f"⚠️ [API] Error searching conversations for task_id {task_id}: {e}")
            
            # If still not found, try to find project by reconstructing path
            # Project paths are typically: workspace/project_{task_id} or workspace/project_{project_name}
            import os
            from mgx_backend.config import Config
            
            # Get workspace from config - resolve to absolute path
            config = Config.default()
            workspace_str = config.project.workspace if hasattr(config.project, 'workspace') else "./workspace"
            
            # Get the script's directory (where api.py is located)
            # api.py is in: workspace/mgx_backend/api.py
            # workspace directory is: workspace/workspace/
            script_dir = Path(__file__).parent.resolve()  # mgx_backend directory
            workspace_root = script_dir.parent  # workspace/ directory (where mgx_backend is)
            
            # Try multiple path resolutions
            workspace_candidates = [
                workspace_root / workspace_str.lstrip("./"),  # workspace/workspace
                workspace_root / "workspace",  # workspace/workspace (fallback)
                Path(workspace_str).resolve() if Path(workspace_str).is_absolute() else workspace_root / workspace_str.lstrip("./"),
                Path(os.getcwd()) / workspace_str.lstrip("./"),
                Path(os.getcwd()) / "workspace",
            ]
            
            workspace = None
            for ws_candidate in workspace_candidates:
                if ws_candidate.exists() and ws_candidate.is_dir():
                    workspace = ws_candidate.resolve()
                    break
            
            if not workspace:
                workspace = workspace_root / "workspace"
                print(f"⚠️ [API] Workspace not found, using default: {workspace}")
            
            print(f"📁 [API] Using workspace: {workspace} (exists: {workspace.exists()}, script_dir: {script_dir}, workspace_root: {workspace_root})")
            
            # Try standard pattern: workspace/project_{task_id}
            potential_path = workspace / f"project_{task_id}"
            if potential_path.exists() and potential_path.is_dir():
                project_path = str(potential_path.resolve())
                print(f"📁 [API] Found project_path from filesystem: {project_path}")
            else:
                # Try to find in workspace directory by matching task_id in directory name
                if workspace.exists():
                    # Look for directories matching the pattern
                    for project_dir in workspace.iterdir():
                        if project_dir.is_dir() and task_id in project_dir.name:
                            project_path = str(project_dir.resolve())
                            print(f"📁 [API] Found project_path by pattern match: {project_path}")
                            break
                
                if not project_path:
                    # List available projects for debugging
                    if workspace.exists():
                        available_projects = [d.name for d in workspace.iterdir() if d.is_dir() and d.name.startswith("project_")]
                        print(f"❌ [API] Project not found for task_id: {task_id}")
                        print(f"   Workspace: {workspace}")
                        print(f"   Available projects: {available_projects[:5]}")
                        print(f"   Looking for: project_{task_id}")
                    # Return empty files instead of 404 for better UX
                    print(f"⚠️ [API] Returning empty files for task_id: {task_id} (project not found)")
                    return {"files": []}
    
    if not project_path:
        # Return empty files instead of 404
        print(f"⚠️ [API] No project_path found for task_id: {task_id}, returning empty files")
        return {"files": []}
    
    # Check if project path exists
    if not Path(project_path).exists():
        # Return empty files instead of 404 if path doesn't exist
        print(f"⚠️ [API] Project path exists in DB but not on disk: {project_path}, returning empty files")
        return {"files": []}
    
    repo = ProjectRepo(project_path)
    
    files = []
    project_root = Path(project_path)
    
    # Get ALL files from the project directory (including src, docs, and root)
    for file_path in project_root.rglob("*"):
        if file_path.is_file():
            rel_path = file_path.relative_to(project_root)
            rel_path_str = str(rel_path)
            
            # Skip hidden files and common build artifacts
            if rel_path.name.startswith('.') or rel_path.suffix in ['.pyc', '.pyo', '.pycache'] or '__pycache__' in rel_path_str:
                continue
            
            # Skip common build/dependency directories
            if any(skip_dir in rel_path_str for skip_dir in ['node_modules', '.git', 'dist', 'build', '.next', '.venv', 'venv', 'env']):
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Determine file type
                file_type = "source"
                if rel_path_str.startswith("docs/"):
                    file_type = "document"
                elif rel_path.suffix in ['.md', '.txt', '.rst']:
                    file_type = "document"
                elif rel_path.suffix in ['.js', '.ts', '.jsx', '.tsx', '.py', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php', '.swift', '.kt']:
                    file_type = "source"
                elif rel_path.suffix in ['.html', '.css', '.scss', '.sass', '.less', '.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.conf']:
                    file_type = "source"
                elif rel_path.suffix in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp']:
                    file_type = "image"
                elif rel_path.suffix in ['.pdf', '.doc', '.docx']:
                    file_type = "document"
                else:
                    file_type = "source"
                
                files.append({
                    "path": rel_path_str,
                    "content": content,
                    "type": file_type
                })
            except Exception as e:
                # For binary files or files that can't be read as text, skip them
                print(f"⚠️ [API] Skipping file {file_path}: {e}")
                continue
    
    return {"files": files}


@app.get("/api/download/{task_id}")
async def download_project(task_id: str):
    """Download the generated project as a zip file."""
    project_path = None
    
    # Get task from database
    task_dict = get_task_dict(task_id)
    if task_dict:
        if task_dict["status"] != "completed":
            raise HTTPException(status_code=400, detail="Task not completed")
        if task_dict.get("result") and task_dict["result"].get("project_path"):
            project_path = task_dict["result"]["project_path"]
    
    if not project_path:
        # Try to get from database by project_id (if task_id is numeric)
        try:
            project_id = int(task_id)
            db = get_db_manager()
            project = db.get_project(project_id)
            if project and project.project_path:
                project_path = project.project_path
                print(f"📁 [API] Found project_path from database by project_id: {project_path}")
        except (ValueError, TypeError):
            # task_id is not numeric (UUID), try to find project by searching conversations
            db = get_db_manager()
            try:
                from mgx_backend.database import ConversationHistoryModel, get_db
                
                db_session = next(get_db())
                try:
                    # Find conversation with this task_id in extra_data
                    all_conversations = db_session.query(ConversationHistoryModel).all()
                    matching_conversation = None
                    for conv in all_conversations:
                        if conv.extra_data and isinstance(conv.extra_data, dict):
                            if conv.extra_data.get("task_id") == task_id:
                                matching_conversation = conv
                                break
                    
                    if matching_conversation and matching_conversation.project_id:
                        project = db.get_project(matching_conversation.project_id)
                        if project and project.project_path:
                            project_path = project.project_path
                            print(f"📁 [API] Found project_path from conversation: {project_path}")
                finally:
                    db_session.close()
            except Exception as e:
                print(f"⚠️ [API] Error searching conversations for task_id {task_id}: {e}")
            
            # If still not found, try to find project by reconstructing path
            if not project_path:
                import os
                from mgx_backend.config import Config
                
                config = Config.default()
                workspace_str = config.project.workspace if hasattr(config.project, 'workspace') else "./workspace"
                
                script_dir = Path(__file__).parent.resolve()
                workspace_root = script_dir.parent
                
                workspace_candidates = [
                    workspace_root / workspace_str.lstrip("./"),
                    workspace_root / "workspace",
                    Path(workspace_str).resolve() if Path(workspace_str).is_absolute() else workspace_root / workspace_str.lstrip("./"),
                    Path(os.getcwd()) / workspace_str.lstrip("./"),
                    Path(os.getcwd()) / "workspace",
                ]
                
                workspace = None
                for ws_candidate in workspace_candidates:
                    if ws_candidate.exists() and ws_candidate.is_dir():
                        workspace = ws_candidate.resolve()
                        break
                
                if not workspace:
                    workspace = workspace_root / "workspace"
                
                # Try standard pattern: workspace/project_{task_id}
                potential_path = workspace / f"project_{task_id}"
                if potential_path.exists() and potential_path.is_dir():
                    project_path = str(potential_path.resolve())
                    print(f"📁 [API] Found project_path from filesystem: {project_path}")
                else:
                    # Try to find in workspace directory by matching task_id in directory name
                    if workspace.exists():
                        for project_dir in workspace.iterdir():
                            if project_dir.is_dir() and task_id in project_dir.name:
                                project_path = str(project_dir.resolve())
                                print(f"📁 [API] Found project_path by pattern match: {project_path}")
                                break
    
    if not project_path:
        raise HTTPException(status_code=404, detail="Project path not found")
    
    project_path = Path(project_path)
    if not project_path.exists():
        # Try to provide more helpful error message
        print(f"❌ [API] Project path does not exist: {project_path}")
        print(f"   Current working directory: {Path.cwd()}")
        print(f"   Absolute path: {project_path.resolve() if project_path.is_absolute() else Path.cwd() / project_path}")
        
        # Check if it's a relative path issue
        if not project_path.is_absolute():
            # Try to resolve relative path
            resolved_path = Path.cwd() / project_path
            if resolved_path.exists():
                project_path = resolved_path
                print(f"✅ [API] Found project using resolved path: {project_path}")
            else:
                # Try from script directory
                script_dir = Path(__file__).parent.parent
                resolved_path = script_dir / project_path
                if resolved_path.exists():
                    project_path = resolved_path
                    print(f"✅ [API] Found project using script-relative path: {project_path}")
                else:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Project files not found on disk. Path: {project_path}. This may happen if the project was deleted or the server was restarted."
                    )
        else:
            raise HTTPException(
                status_code=404, 
                detail=f"Project files not found on disk. Path: {project_path}. This may happen if the project was deleted or the server was restarted."
            )
    
    # Create zip file
    zip_path = f"/tmp/{task_id}.zip"
    try:
        shutil.make_archive(zip_path.replace('.zip', ''), 'zip', project_path)
    except Exception as e:
        print(f"❌ [API] Failed to create zip file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create zip file: {str(e)}")
    
    if not Path(zip_path).exists():
        raise HTTPException(status_code=500, detail="Zip file was not created")
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"project_{task_id}.zip"
    )


@app.get("/api/tasks")
async def list_tasks():
    """List all tasks."""
    db = get_db_manager()
    tasks_list = db.list_tasks()
    return {"tasks": [get_task_dict(task.task_id) for task in tasks_list]}


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task."""
    task_dict = get_task_dict(task_id)
    if not task_dict:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Delete project files
    if task_dict.get("result") and task_dict["result"].get("project_path"):
        project_path = Path(task_dict["result"]["project_path"])
        if project_path.exists():
            shutil.rmtree(project_path)
    
    # Delete from database
    db = get_db_manager()
    db.delete_task(task_id)
    return {"message": "Task deleted"}


@app.post("/api/github/upload")
async def upload_to_github(request: GitHubUploadRequest):
    """Upload project to GitHub repository."""
    task_dict = get_task_dict(request.task_id)
    if not task_dict:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_dict["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    if not task_dict.get("result") or not task_dict["result"].get("project_path"):
        raise HTTPException(status_code=404, detail="Project path not found")
    
    project_path = Path(task_dict["result"]["project_path"])
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project files not found")
    
    try:
        import httpx
        
        # Initialize git repository if not already initialized
        if not (project_path / ".git").exists():
            subprocess.run(["git", "init"], cwd=project_path, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "MGX Bot"], cwd=project_path, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "mgx@example.com"], cwd=project_path, check=True, capture_output=True)
        
        # Create .gitignore if it doesn't exist
        gitignore_path = project_path / ".gitignore"
        if not gitignore_path.exists():
            gitignore_path.write_text("__pycache__/\n*.pyc\n*.pyo\n*.pyd\n.Python\nenv/\nvenv/\n.venv/\n*.log\n.DS_Store\n")
        
        # Add all files and commit
        subprocess.run(["git", "add", "."], cwd=project_path, check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit from MGX"], cwd=project_path, check=True, capture_output=True)
        
        # Create repository on GitHub using GitHub API
        async with httpx.AsyncClient() as client:
            # Determine token type (fine-grained tokens start with github_pat_, classic tokens start with ghp_)
            is_fine_grained = request.github_token.startswith("github_pat_")
            
            # For fine-grained tokens, we need to get the owner first
            if is_fine_grained:
                # Get user info to determine owner
                user_response = await client.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"Bearer {request.github_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28"
                    }
                )
                if user_response.status_code != 200:
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Failed to get GitHub user info: {user_response.text}. Please check your token permissions."
                    )
                user_data = user_response.json()
                owner = user_data["login"]
                
                # For fine-grained tokens, we need to use the organization/user endpoint
                # Try user endpoint first
                create_repo_response = await client.post(
                    f"https://api.github.com/user/repos",
                    headers={
                        "Authorization": f"Bearer {request.github_token}",
                        "Accept": "application/vnd.github+json",
                        "X-GitHub-Api-Version": "2022-11-28"
                    },
                    json={
                        "name": request.repo_name,
                        "description": request.description,
                        "private": request.is_private,
                        "auto_init": False
                    }
                )
                
                # If that fails with 403, the token might not have repository creation permissions
                if create_repo_response.status_code == 403:
                    error_detail = create_repo_response.text
                    raise HTTPException(
                        status_code=403,
                        detail=f"Fine-grained token missing required permissions. Please ensure your token has 'Administration: Write' permission for repository creation. Error: {error_detail}"
                    )
            else:
                # Classic token - use traditional API
                create_repo_response = await client.post(
                    "https://api.github.com/user/repos",
                    headers={
                        "Authorization": f"token {request.github_token}",
                        "Accept": "application/vnd.github.v3+json"
                    },
                    json={
                        "name": request.repo_name,
                        "description": request.description,
                        "private": request.is_private,
                        "auto_init": False
                    }
                )
            
            if create_repo_response.status_code not in [200, 201]:
                error_msg = create_repo_response.text
                raise HTTPException(
                    status_code=create_repo_response.status_code,
                    detail=f"Failed to create GitHub repository: {error_msg}"
                )
            
            repo_data = create_repo_response.json()
            repo_url = repo_data["clone_url"]
            
            # Get GitHub username from token (if not already obtained for fine-grained tokens)
            if not is_fine_grained:
                user_response = await client.get(
                    "https://api.github.com/user",
                    headers={
                        "Authorization": f"token {request.github_token}",
                        "Accept": "application/vnd.github.v3+json"
                    }
                )
                if user_response.status_code != 200:
                    raise HTTPException(status_code=500, detail="Failed to get GitHub user info")
                user_data = user_response.json()
                username = user_data["login"]
            else:
                username = owner
            
            # Add remote and push
            remote_url = repo_url.replace("https://", f"https://{request.github_token}@")
            subprocess.run(
                ["git", "remote", "add", "origin", remote_url],
                cwd=project_path,
                check=True,
                capture_output=True
            )
            
            # Push to GitHub
            push_result = subprocess.run(
                ["git", "push", "-u", "origin", "main"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            # If main branch doesn't exist, try master
            if push_result.returncode != 0:
                # Get current branch name
                branch_result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
                current_branch = branch_result.stdout.strip() or "master"
                
                # Rename branch to main if needed
                if current_branch != "main":
                    subprocess.run(
                        ["git", "branch", "-M", "main"],
                        cwd=project_path,
                        check=True,
                        capture_output=True
                    )
                
                # Try pushing again
                push_result = subprocess.run(
                    ["git", "push", "-u", "origin", "main"],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
            
            if push_result.returncode != 0:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to push to GitHub: {push_result.stderr}"
                )
            
            return {
                "success": True,
                "repo_url": repo_data["html_url"],
                "clone_url": repo_url,
                "message": f"Successfully uploaded to GitHub: {repo_data['html_url']}"
            }
            
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Git operation failed: {e.stderr.decode() if e.stderr else str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload to GitHub: {str(e)}"
        )


# ==================== Authentication & User Management ====================

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


@app.post("/api/auth/register", response_model=Token)
async def register(user_data: UserRegister):
    """Register a new user."""
    db = get_db_manager()
    
    # Check if username already exists
    if db.get_user_by_username(user_data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email already exists
    if db.get_user_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    from mgx_backend.database import UserCreate
    password_hash = get_password_hash(user_data.password)
    user_create = UserCreate(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )
    user = db.create_user(user_create, password_hash)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@app.post("/api/auth/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user and return JWT token."""
    user = await authenticate_user(user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.model_validate(user)
    }


@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserModel = Depends(get_current_user)):
    """Get current user information."""
    return UserResponse.model_validate(current_user)


@app.put("/api/auth/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user)
):
    """Update current user information."""
    db = get_db_manager()
    updated_user = db.update_user(current_user.id, user_update)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(updated_user)


# ==================== Conversation History ====================

@app.post("/api/conversations", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    current_user: UserModel = Depends(get_current_user)
):
    """Create a new conversation."""
    # Ensure user_id matches current user (override any user_id in request)
    conversation.user_id = current_user.id
    
    db = get_db_manager()
    db_conv = db.create_conversation(conversation)
    return ConversationResponse.model_validate(db_conv)


@app.get("/api/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    project_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_user)
):
    """List conversations for current user."""
    db = get_db_manager()
    conversations = db.list_conversations(
        user_id=current_user.id,
        project_id=project_id,
        skip=skip,
        limit=limit
    )
    return [ConversationResponse.model_validate(conv) for conv in conversations]


@app.get("/api/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: UserModel = Depends(get_current_user)
):
    """Get a conversation by ID."""
    db = get_db_manager()
    conv = db.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    return ConversationResponse.from_orm(conv)


@app.put("/api/conversations/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_update: ConversationUpdate,
    current_user: UserModel = Depends(get_current_user)
):
    """Update a conversation."""
    db = get_db_manager()
    conv = db.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conv.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    updated_conv = db.update_conversation(conversation_id, conversation_update)
    return ConversationResponse.from_orm(updated_conv)


@app.delete("/api/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: UserModel = Depends(get_current_user)
):
    """Delete a conversation."""
    db = get_db_manager()
    success = db.delete_conversation(conversation_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)