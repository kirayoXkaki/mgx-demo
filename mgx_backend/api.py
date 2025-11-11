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


class GenerateRequest(BaseModel):
    idea: str
    investment: float = 5.0
    n_round: int = 5


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
            "progress": 10
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
            "progress": 20
        })
        
        # Progress callback for real-time updates
        async def progress_callback(update: dict):
            """Callback for progress updates from team execution."""
            update_type = update.get("type", "progress")
            role = update.get("role", "")
            action = update.get("action", "")
            stage = update.get("stage", "")
            message = update.get("message", "")
            
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
            
            await send_progress(task_id, {
                "type": update_type,
                "role": role,
                "action": action,
                "stage": stage,
                "progress": progress,
                "message": message
            })
        
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
                    await repo.save_code_files(message.content)
                    print("✅ Code saved")
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
        
        # Keep connection alive
        while True:
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        if task_id in websocket_connections:
            del websocket_connections[task_id]


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)