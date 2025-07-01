from sqlalchemy.orm import Session

from app.repositories.event_log_repository import event_log_repository
from app.schemas.password_reset import UserEvent


class EventService:
    """
    Service for handling event logic
    """
    
    async def log_user_event(self, db: Session, event: UserEvent) -> bool:
        """
        Log user event to database
        """
        try:
            event_log_repository.create_event_log(
                db=db,
                event_id=str(event.event_id),
                event_type=event.event_type,
                payload=event.payload
            )
            return True
        except Exception:
            return False


# Singleton instance
event_service = EventService()
