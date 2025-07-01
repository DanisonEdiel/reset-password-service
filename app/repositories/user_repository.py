from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.models.user import User


class UserRepository:
    """
    Repository for User model to handle database operations
    """
    
    def get_by_id(self, db: Session, user_id: UUID) -> Optional[User]:
        """
        Get user by ID
        """
        return db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get user by email
        """
        return db.query(User).filter(User.email == email).first()
    
    def update_password(self, db: Session, user: User, new_password: str) -> User:
        """
        Update user password
        """
        user.hashed_password = get_password_hash(new_password)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


# Singleton instance
user_repository = UserRepository()
