"""
Database initialization script
"""
import logging

from app.db.database import engine
from app.db.init_db import init_db, get_db_session
from app.models.event_log import EventLog
from app.models.password_reset import PasswordResetToken

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Initialize database tables
    """
    logger.info("Creating database tables...")
    init_db()
    logger.info("Database tables created successfully!")


if __name__ == "__main__":
    main()
