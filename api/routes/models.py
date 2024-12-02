# api/routes/models.py

from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

# User models
class User(BaseModel):
    user_id: Optional[uuid.UUID] = None
    username: str
    email: str
    bio: Optional[str] = None
    profile_pic: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    bio: Optional[str] = None
    profile_pic: Optional[str] = None

class UserInDB(User):
    hashed_password: str

# Group model
class Group(BaseModel):
    group_id: Optional[uuid.UUID] = None
    group_name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: uuid.UUID

# Post model
class Post(BaseModel):
    post_id: Optional[uuid.UUID] = None
    user_id: uuid.UUID
    group_id: uuid.UUID
    content: str
    created_at: Optional[datetime] = None

# Comment model
class Comment(BaseModel):
    comment_id: Optional[uuid.UUID] = None
    post_id: uuid.UUID
    user_id: uuid.UUID
    content: str
    created_at: Optional[datetime] = None

# Message model
class Message(BaseModel):
    message_id: Optional[uuid.UUID] = None
    sender_id: uuid.UUID
    receiver_id: uuid.UUID
    content: str
    created_at: Optional[datetime] = None
