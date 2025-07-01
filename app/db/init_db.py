from sqlalchemy.orm import Session

from app.db.database import Base, engine
from app.models.user import User
from app.models.password_reset import PasswordResetToken
from app.models.event_log import EventLog


def init_db() -> None:
    """
    Initialize database tables
    """
    # Create tables
    Base.metadata.create_all(bind=engine)


def get_db_session() -> Session:
    """
    Get database session for initialization
    """
    from app.db.database import SessionLocal
    return SessionLocal()
