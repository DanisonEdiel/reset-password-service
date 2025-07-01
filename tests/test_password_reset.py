import uuid
from unittest.mock import patch, AsyncMock

import pytest
from fastapi import status

from app.models.user import User
from app.core.security import get_password_hash
from app.schemas.password_reset import UserRegisteredEvent


@pytest.fixture
def test_user(db):
    """Create a test user"""
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        username="testuser",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/password/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "ok", "service": "reset-password-service"}


@patch("app.services.password_reset_service.email_service.send_password_reset_email")
@patch("app.services.password_reset_service.event_publisher.publish_password_reset_requested")
def test_request_password_reset(mock_publish, mock_send_email, client, test_user):
    """Test password reset request endpoint"""
    # Mock email sending and event publishing
    mock_send_email.return_value = AsyncMock(return_value=True)()
    mock_publish.return_value = AsyncMock(return_value=True)()
    
    # Test with existing user
    response = client.post(
        "/password/reset-request",
        json={"email": "test@example.com"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()
    assert "email" in response.json()
    assert response.json()["email"] == "test@example.com"
    
    # Test with non-existing user (should still return 200 to prevent email enumeration)
    response = client.post(
        "/password/reset-request",
        json={"email": "nonexistent@example.com"}
    )
    assert response.status_code == status.HTTP_200_OK
    assert "message" in response.json()
    assert "email" in response.json()
    assert response.json()["email"] == "nonexistent@example.com"


def test_user_registered_event(client):
    """Test user registered event endpoint"""
    event_data = {
        "event_id": str(uuid.uuid4()),
        "event_type": "user-registered",
        "payload": {
            "user_id": str(uuid.uuid4()),
            "email": "user@example.com",
            "timestamp": "2023-01-01T00:00:00Z"
        }
    }
    
    response = client.post(
        "/password/events/user-registered",
        json=event_data
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["status"] == "success"
