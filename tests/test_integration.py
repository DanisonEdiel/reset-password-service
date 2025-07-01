"""
Integration tests for the reset password service
"""
import uuid
from unittest.mock import patch, AsyncMock

import pytest
from fastapi import status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.core.security import get_password_hash, generate_reset_token
from app.repositories.password_reset_repository import password_reset_repository
from datetime import datetime, timedelta


@pytest.fixture
def active_reset_token(db: Session, test_user: User):
    """Create an active reset token for testing"""
    token_str = generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(minutes=30)
    
    token = PasswordResetToken(
        user_id=test_user.id,
        token=token_str,
        expires_at=expires_at,
        is_used=False
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


@pytest.fixture
def expired_reset_token(db: Session, test_user: User):
    """Create an expired reset token for testing"""
    token_str = generate_reset_token()
    expires_at = datetime.utcnow() - timedelta(minutes=5)
    
    token = PasswordResetToken(
        user_id=test_user.id,
        token=token_str,
        expires_at=expires_at,
        is_used=False
    )
    db.add(token)
    db.commit()
    db.refresh(token)
    return token


def test_reset_confirm_success(client, active_reset_token):
    """Test successful password reset confirmation"""
    response = client.post(
        "/password/reset-confirm",
        json={
            "token": active_reset_token.token,
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True
    assert "Password reset successfully" in response.json()["message"]


def test_reset_confirm_expired_token(client, expired_reset_token):
    """Test password reset with expired token"""
    response = client.post(
        "/password/reset-confirm",
        json={
            "token": expired_reset_token.token,
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Token expired" in response.json()["detail"]


def test_reset_confirm_invalid_token(client):
    """Test password reset with invalid token"""
    response = client.post(
        "/password/reset-confirm",
        json={
            "token": "invalid-token",
            "new_password": "newpassword123"
        }
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Invalid token" in response.json()["detail"]
