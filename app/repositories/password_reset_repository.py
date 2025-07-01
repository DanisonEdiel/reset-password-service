from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.password_reset import PasswordResetToken
from app.models.user import User


class PasswordResetRepository:
    """
    Repository for PasswordResetToken model to handle database operations
    """
    
    def create_token(self, db: Session, user: User, token: str) -> PasswordResetToken:
        """
        Create a new password reset token
        """
        # Set expiration time
        expires_at = datetime.utcnow() + timedelta(minutes=settings.RESET_TOKEN_EXPIRE_MINUTES)
        
        # Create token
        db_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
            is_used=False
        )
        db.add(db_token)
        db.commit()
        db.refresh(db_token)
        return db_token
    
    def get_by_token(self, db: Session, token: str) -> Optional[PasswordResetToken]:
        """
        Get password reset token by token string
        """
        return db.query(PasswordResetToken).filter(PasswordResetToken.token == token).first()
    
    def invalidate_token(self, db: Session, token: PasswordResetToken) -> PasswordResetToken:
        """
        Mark token as used
        """
        token.is_used = True
        db.add(token)
        db.commit()
        db.refresh(token)
        return token
    
    def invalidate_user_tokens(self, db: Session, user_id: UUID) -> None:
        """
        Invalidate all tokens for a user
        """
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user_id,
            PasswordResetToken.is_used == False
        ).update({"is_used": True})
        db.commit()


# Singleton instance
password_reset_repository = PasswordResetRepository()
