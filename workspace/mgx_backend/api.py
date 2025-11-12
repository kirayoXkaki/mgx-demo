"""FastAPI backend wrapper for MGX Backend."""

import asyncio
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
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


app = FastAPI(title="MGX Backend API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Task storage
tasks: Dict[str, dict] = {}
websocket_connections: Dict[str, WebSocket] = {}
# Message queue for messages sent before WebSocket connection is established
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


async def send_progress(task_id: str, data: dict):
    """Send progress update via WebSocket."""
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
    try:
        tasks[task_id]["status"] = "running"
        tasks[task_id]["current_stage"] = "Initializing"
        tasks[task_id]["updated_at"] = datetime.now().isoformat()
        
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
        
        tasks[task_id]["progress"] = 20
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
                progress = tasks[task_id].get("progress", 20)
            
            tasks[task_id]["progress"] = progress
            tasks[task_id]["current_stage"] = stage
            
            # Update cost in real-time from context
            current_cost = ctx.cost_manager.total_cost
            tasks[task_id]["cost"] = current_cost
            
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
        tasks[task_id]["current_stage"] = "Starting team collaboration..."
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
            tasks[task_id]["progress"] = min(progress, 90)  # Cap at 90% until saving
            tasks[task_id]["current_stage"] = stage
        
        # Save outputs
        tasks[task_id]["current_stage"] = "Saving project files..."
        tasks[task_id]["progress"] = 90
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
        
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["progress"] = 100
        tasks[task_id]["current_stage"] = "Completed"
        tasks[task_id]["cost"] = ctx.cost_manager.total_cost
        tasks[task_id]["result"] = {
            "project_path": str(ctx.project_path),
            "files": repo.srcs.all_files,
            "docs": repo.docs.all_files,
            "cost": ctx.cost_manager.total_cost,
            "tokens": ctx.cost_manager.total_tokens
        }
        tasks[task_id]["updated_at"] = datetime.now().isoformat()
        
        await send_progress(task_id, {
            "type": "complete",
            "status": "completed",
            "progress": 100,
            "cost": tasks[task_id]["cost"],
            "result": tasks[task_id]["result"]
        })
        
    except Exception as e:
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["error"] = str(e)
        tasks[task_id]["updated_at"] = datetime.now().isoformat()
        
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
    
    tasks[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0,
        "current_stage": "Queued",
        "cost": 0.0,
        "idea": request.idea,
        "investment": request.investment,
        "n_round": request.n_round,
        "result": None,
        "error": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
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
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return tasks[task_id]


@app.websocket("/api/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for real-time updates."""
    await websocket.accept()
    websocket_connections[task_id] = websocket
    
    try:
        # Send initial status (format matches frontend expectations)
        if task_id in tasks:
            task = tasks[task_id]
            await websocket.send_json({
                "type": "status",
                "status": task.get("status", "pending"),
                "progress": task.get("progress", 0),
                "stage": task.get("current_stage", "Queued"),
                "cost": task.get("cost", 0.0),
                "result": task.get("result"),
                "error": task.get("error")
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
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    project_path = task["result"]["project_path"]
    repo = ProjectRepo(project_path)
    
    files = []
    
    # Get all files with content
    for file_path in repo.srcs.all_files:
        full_path = repo.srcs.path / file_path
        if full_path.exists():
            content = full_path.read_text(encoding='utf-8', errors='ignore')
            files.append({
                "path": f"src/{file_path}",
                "content": content,
                "type": "source"
            })
    
    for doc_type in ["prd", "system_design"]:
        doc_repo = getattr(repo.docs, doc_type)
        for file_path in doc_repo.all_files:
            full_path = doc_repo.path / file_path
            if full_path.exists():
                content = full_path.read_text(encoding='utf-8', errors='ignore')
                files.append({
                    "path": f"docs/{doc_type}/{file_path}",
                    "content": content,
                    "type": "document"
                })
    
    # Also get files from project root (non-src, non-docs files)
    project_root = Path(project_path)
    for file_path in project_root.rglob("*"):
        if file_path.is_file():
            # Skip files already in src or docs
            rel_path = file_path.relative_to(project_root)
            rel_path_str = str(rel_path)
            if rel_path_str.startswith("src/") or rel_path_str.startswith("docs/"):
                continue
            
            # Skip hidden files and common build artifacts
            if rel_path.name.startswith('.') or rel_path.suffix in ['.pyc', '.pyo'] or '__pycache__' in rel_path_str:
                continue
            
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            # Use normalized path (same as what's sent in streaming)
            files.append({
                "path": rel_path_str,
                "content": content,
                "type": "source" if rel_path.suffix in ['.js', '.ts', '.jsx', '.tsx', '.py', '.html', '.css', '.json'] else "document"
                })
    
    return {"files": files}


@app.get("/api/download/{task_id}")
async def download_project(task_id: str):
    """Download the generated project as a zip file."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    project_path = Path(task["result"]["project_path"])
    if not project_path.exists():
        raise HTTPException(status_code=404, detail="Project files not found")
    
    # Create zip file
    zip_path = f"/tmp/{task_id}.zip"
    shutil.make_archive(zip_path.replace('.zip', ''), 'zip', project_path)
    
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"project_{task_id}.zip"
    )


@app.get("/api/tasks")
async def list_tasks():
    """List all tasks."""
    return {"tasks": list(tasks.values())}


@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str):
    """Delete a task."""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Delete project files
    task = tasks[task_id]
    if task.get("result") and task["result"].get("project_path"):
        project_path = Path(task["result"]["project_path"])
        if project_path.exists():
            shutil.rmtree(project_path)
    
    del tasks[task_id]
    return {"message": "Task deleted"}


@app.post("/api/github/upload")
async def upload_to_github(request: GitHubUploadRequest):
    """Upload project to GitHub repository."""
    if request.task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = tasks[request.task_id]
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="Task not completed")
    
    project_path = Path(task["result"]["project_path"])
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)