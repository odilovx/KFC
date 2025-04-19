from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    timestamp: datetime
    user_id: int

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    messages: List[Message] = []

    class Config:
        from_attributes = True 