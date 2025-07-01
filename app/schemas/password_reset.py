import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetTokenResponse(BaseModel):
    """Schema for password reset token response"""
    message: str
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)


class PasswordResetResult(BaseModel):
    """Schema for password reset result"""
    success: bool
    message: str


class UserEvent(BaseModel):
    """Schema for user event"""
    event_id: uuid.UUID
    event_type: str
    payload: dict


class UserRegisteredEvent(BaseModel):
    """Schema for user registered event"""
    event_id: uuid.UUID
    event_type: str = "user-registered"
    payload: dict
    
    class Config:
        schema_extra = {
            "example": {
                "event_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "event_type": "user-registered",
                "payload": {
                    "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "email": "user@example.com",
                    "timestamp": "2023-01-01T00:00:00Z"
                }
            }
        }
