from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from backend.database import get_db
from backend.models.models import Task, Bot
from backend.schemas.schemas import TaskCreate, TaskResponse, TaskStats
import bot_service.worker as worker

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    # Verify bot exists
    bot = db.query(Bot).filter(Bot.id == task.bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
        
    db_task = Task(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.post("/send-message", response_model=TaskResponse)
def send_message_task(task: TaskCreate, db: Session = Depends(get_db)):
    # Same as create_task
    return create_task(task, db)

@router.get("/stats", response_model=TaskStats)
def get_task_stats(db: Session = Depends(get_db)):
    total = db.query(func.count(Task.id)).scalar() or 0
    pending = db.query(func.count(Task.id)).filter(Task.status == "pending").scalar() or 0
    done = db.query(func.count(Task.id)).filter(Task.status == "done").scalar() or 0
    failed = db.query(func.count(Task.id)).filter(Task.status == "failed").scalar() or 0
    
    return TaskStats(
        total=total,
        pending=pending,
        done=done,
        failed=failed
    )



@router.post("/process-now")
def process_now(background_tasks: BackgroundTasks):
    """Trigger a one-shot processing run in the background.

    This schedules `bot_service.worker.run_process_pending_once` so the
    HTTP request returns immediately while processing runs in the background.
    """
    # Schedule the synchronous wrapper which will run the async one-shot
    background_tasks.add_task(worker.run_process_pending_once)
    return {"status": "scheduled"}
