from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.models import Bot
from backend.schemas.schemas import BotCreate, BotResponse

router = APIRouter(prefix="/api/bots")

@router.get("/", response_model=list[BotResponse])
def get_bots(db: Session = Depends(get_db)):
    return db.query(Bot).all()

@router.post("/", response_model=BotResponse)
def create_bot(bot: BotCreate, db: Session = Depends(get_db)):
    db_bot = Bot(**bot.dict())
    db.add(db_bot)
    db.commit()
    db.refresh(db_bot)
    return db_bot
