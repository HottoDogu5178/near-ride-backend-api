from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    class Config:
        orm_mode = True

class ProfileCreate(BaseModel):
    display_name: Optional[str]
    gender: Optional[str]
    birthday: Optional[date]
    bio: Optional[str]
    avatar_url: Optional[str]
    location: Optional[str]

class ProfileOut(ProfileCreate):
    id: int
    user_id: int
    class Config:
        orm_mode = True

class MatchOut(BaseModel):
    id: int
    user1_id: int
    user2_id: int
    matched_at: datetime
    class Config:
        orm_mode = True

class MessageCreate(BaseModel):
    match_id: int
    sender_id: int
    content: str

class MessageOut(BaseModel):
    id: int
    match_id: int
    sender_id: int
    content: str
    sent_at: datetime
    class Config:
        orm_mode = True
