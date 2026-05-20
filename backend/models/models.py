# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
# pyrefly: ignore [missing-import]
from datetime import datetime
from backend.database import Base

class Bot(Base):
    __tablename__ = "bots"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String)
    name = Column(String)
    is_active = Column(Boolean, default=True)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    bot_id = Column(Integer, ForeignKey("bots.id"))
    status = Column(String, default="pending", index=True)
    target_id = Column(String)
    message = Column(String)
    error_message = Column(String, nullable=True)
    completed_at = Column(String, nullable=True)

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