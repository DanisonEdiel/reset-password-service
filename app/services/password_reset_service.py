from datetime import datetime
from typing import Optional, Tuple

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.events import event_publisher
from app.core.security import generate_reset_token, get_password_hash
from app.db.database import get_db
from app.models.user import User
from app.repositories.password_reset_repository import password_reset_repository
from app.repositories.user_repository import user_repository
from app.services.email_service import email_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")


class PasswordResetService:
    """
    Service for handling password reset logic
    """
    
    async def request_password_reset(self, db: Session, email: str) -> bool:
        """
        Request password reset for user
        """
        # Find user by email
        user = user_repository.get_by_email(db, email=email)
        if not user:
            # We don't want to reveal if the email exists or not for security reasons
            return False
        
        # Invalidate any existing tokens for this user
        password_reset_repository.invalidate_user_tokens(db, user.id)
        
        # Generate new reset token
        token = generate_reset_token()
        
        # Save token to database
        password_reset_repository.create_token(db, user, token)
        
        # Send email with reset token
        email_sent = await email_service.send_password_reset_email(user.email, token)
        
        # Publish event
        if email_sent:
            user_data = {
                "id": user.id,
                "email": user.email,
                "requested_at": datetime.utcnow()
            }
            await event_publisher.publish_password_reset_requested(user_data)
        
        return email_sent
    
    async def reset_password(self, db: Session, token: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset user password using token
        """
        # Find token in database
        db_token = password_reset_repository.get_by_token(db, token)
        if not db_token:
            return False, "Invalid token"
        
        # Check if token is valid
        if not db_token.is_valid():
            return False, "Token expired or already used"
        
        # Get user
        user = user_repository.get_by_id(db, db_token.user_id)
        if not user:
            return False, "User not found"
        
        # Update password
        user_repository.update_password(db, user, new_password)
        
        # Invalidate token
        password_reset_repository.invalidate_token(db, db_token)
        
        # Publish event
        user_data = {
            "id": user.id,
            "email": user.email,
            "reset_at": datetime.utcnow()
        }
        await event_publisher.publish_password_reset_completed(user_data)
        
        return True, "Password reset successfully"
    
    async def get_current_user(
        self, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
    ) -> User:
        """
        Get current authenticated user
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = user_repository.get_by_id(db, user_id=user_id)
        if user is None:
            raise credentials_exception
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
            )
        return user


# Singleton instance
password_reset_service = PasswordResetService()
