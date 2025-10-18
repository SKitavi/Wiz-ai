from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, Dict, Any


class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None
    
    @field_validator('password')
    def validate_password(cls, v):
        # Basic validation (expand as needed)
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for token response"""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    """Schema for user data in responses"""
    id: int
    email: str
    full_name: Optional[str] = None
    is_active: bool
    preferences: Dict[str, Any]
    created_at: str
    
    class Config:
        from_attributes = True


class PasswordChange(BaseModel):
    """Schema for password change"""
    old_password: str
    new_password: str = Field(..., min_length=8)