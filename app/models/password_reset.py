import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class PasswordResetToken(Base):
    """
    Password reset token model for storing password reset requests
    """
    __tablename__ = "password_reset_tokens"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String, nullable=False, index=True)
    is_used = Column(Boolean(), default=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with User model
    user = relationship("User", foreign_keys=[user_id])
    
    def __repr__(self) -> str:
        return f"<PasswordResetToken {self.token[:8]}...>"
    
    def is_valid(self) -> bool:
        """
        Check if token is valid (not used and not expired)
        """
        return not self.is_used and datetime.utcnow() < self.expires_at
