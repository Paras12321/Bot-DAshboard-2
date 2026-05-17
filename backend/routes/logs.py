from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.models import Log
from backend.schemas.schemas import LogResponse

router = APIRouter(prefix="/api/logs", tags=["logs"])

@router.get("/", response_model=List[LogResponse])
def get_logs(limit: int = Query(10, description="Number of logs to return"), db: Session = Depends(get_db)):
    return db.query(Log).order_by(Log.timestamp.desc()).limit(limit).all()
