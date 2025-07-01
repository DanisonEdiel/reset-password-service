from sqlalchemy.orm import Session

from app.models.event_log import EventLog


class EventLogRepository:
    """
    Repository for EventLog model to handle database operations
    """
    
    def create_event_log(self, db: Session, event_id: str, event_type: str, payload: dict) -> EventLog:
        """
        Create a new event log entry
        """
        db_event_log = EventLog(
            event_id=event_id,
            event_type=event_type,
            payload=payload
        )
        db.add(db_event_log)
        db.commit()
        db.refresh(db_event_log)
        return db_event_log


# Singleton instance
event_log_repository = EventLogRepository()
