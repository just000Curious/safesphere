from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    phone: str
    password: str
    role: str = "user"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    phone: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class ContactAdd(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    relationship: str
    is_primary: bool = False

class ContactResponse(BaseModel):
    id: UUID
    name: str
    phone: str
    email: Optional[EmailStr]
    relationship: str
    is_primary: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: UUID
    role: str

class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    role: Optional[str] = None
