from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class AdvertCreate(BaseModel):
    title: str
    description: str
    owner_id: int


class AdvertUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class LoginSchema(BaseModel):
    email: EmailStr
    password: str