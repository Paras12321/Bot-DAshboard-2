# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from typing import Optional, List

class BotCreate(BaseModel):
    name: str
    platform: str
    token: str
    role: Optional[str] = "general"

class BotResponse(BotCreate):
    id: int
    is_active: bool
    created_at: str

    class Config:
        orm_mode = True
        from_attributes = True

class TaskCreate(BaseModel):
    bot_id: int
    target_id: str
    message: str
    action: Optional[str] = "send_message"

class TaskResponse(TaskCreate):
    id: int
    status: str
    error_message: Optional[str]
    completed_at: Optional[str]
    created_at: str

    class Config:
        orm_mode = True
        from_attributes = True

class TaskStats(BaseModel):
    total: int
    pending: int
    done: int
    failed: int

class LogResponse(BaseModel):
    id: int
    task_id: Optional[int]
    bot_id: Optional[int]
    level: str
    message: str
    details: Optional[str]
    timestamp: str

    class Config:
        orm_mode = True
        from_attributes = True

class AutoReplyCreate(BaseModel):
    bot_id: int
    trigger_keyword: str
    response_text: str
    match_type: Optional[str] = "contains"

class AutoReplyResponse(AutoReplyCreate):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
        from_attributes = True

class WelcomeMessageCreate(BaseModel):
    bot_id: int
    channel_id: Optional[str] = "general"
    message_template: str

class WelcomeMessageResponse(WelcomeMessageCreate):
    id: int
    is_active: bool

    class Config:
        orm_mode = True
        from_attributes = True
