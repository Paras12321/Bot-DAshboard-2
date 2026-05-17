from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.models import Bot
from backend.schemas.schemas import BotCreate, BotResponse

router = APIRouter(prefix="/api/bots", tags=["bots"])

@router.get("/", response_model=List[BotResponse])
def get_bots(db: Session = Depends(get_db)):
    return db.query(Bot).all()

@router.post("/", response_model=BotResponse)
def create_bot(bot: BotCreate, db: Session = Depends(get_db)):
    db_bot = Bot(**bot.dict())
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot

@router.patch("/{bot_id}/toggle", response_model=BotResponse)
def toggle_bot(bot_id: int, db: Session = Depends(get_db)):
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    bot.is_active = not bot.is_active
    db.commit()
    db.refresh(bot)
    return bot

@router.delete("/{bot_id}", status_code=204)
def delete_bot(bot_id: int, db: Session = Depends(get_db)):
    bot = db.query(Bot).filter(Bot.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
    db.delete(bot)
    db.commit()
