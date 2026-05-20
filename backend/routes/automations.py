# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException
# pyrefly: ignore [missing-import, parse-error]
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models.models import AutoReply, WelcomeMessage, Bot
from backend.schemas.schemas import AutoReplyCreate, AutoReplyResponse, WelcomeMessageCreate, WelcomeMessageResponse

auto_reply_router = APIRouter(prefix="/api/auto-reply")
welcome_router = APIRouter(prefix="/api/welcome")

@auto_reply_router.get("/", response_model=List[AutoReplyResponse])
def get_auto_replies(db: Session = Depends(get_db)):
    return db.query(AutoReply).all()

@auto_reply_router.post("/", response_model=AutoReplyResponse)
def create_auto_reply(rule: AutoReplyCreate, db: Session = Depends(get_db)):
    bot = db.query(Bot).filter(Bot.id == rule.bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
        
    db_rule = AutoReply(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@auto_reply_router.delete("/{rule_id}", status_code=204)
def delete_auto_reply(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(AutoReply).filter(AutoReply.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()

@welcome_router.post("/", response_model=WelcomeMessageResponse)
def create_welcome_message(msg: WelcomeMessageCreate, db: Session = Depends(get_db)):
    bot = db.query(Bot).filter(Bot.id == msg.bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")
        
    db_msg = WelcomeMessage(**msg.dict())
    db.add(db_msg)
    db.commit()
    db.refresh(db_msg)
    return db_msg
