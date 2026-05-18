# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
from datetime import datetime

from backend.database import Base

class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True) # 'discord' or 'telegram'
    token = Column(String)
    name = Column(String)
    role = Column(String, default="general")
    is_active = Column(Boolean, default=True)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"))
    status = Column(String, default="pending", index=True) # pending, done, failed
    target_id = Column(String) # Channel ID or User ID
    message = Column(String)
    action = Column(String, default="send_message")
    error_message = Column(String, nullable=True)
    completed_at = Column(String, nullable=True)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())

class Log(Base):
    __tablename__ = "logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    bot_id = Column(Integer, ForeignKey("bots.id"), nullable=True)
    level = Column(String, default="info") # info, success, error
    message = Column(String)
    details = Column(String, nullable=True)
    timestamp = Column(String, default=lambda: datetime.utcnow().isoformat())

class AutoReply(Base):
    __tablename__ = "auto_replies"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"))
    trigger_keyword = Column(String)
    response_text = Column(String)
    match_type = Column(String, default="contains")
    is_active = Column(Boolean, default=True)

class WelcomeMessage(Base):
    __tablename__ = "welcome_messages"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"))
    channel_id = Column(String, default="general")
    message_template = Column(String)
    is_active = Column(Boolean, default=True)