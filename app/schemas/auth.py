from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: Optional[int]
    email: Optional[str]
    username: Optional[str]
    full_name: Optional[str]
    role: Optional[str]
    
    class Config:
        from_attributes = True 