import json
from typing import Any, Dict

import aiokafka
from loguru import logger

from app.core.config import settings


class EventPublisher:
    """
    Event publisher for sending messages to Kafka
    """
    def __init__(self):
        self.producer = None
        self.connected = False
    
    async def connect(self) -> None:
        """
        Connect to Kafka broker
        """
        if self.connected:
            return
        
        try:
            # Extract Kafka connection info from settings
            broker_url = settings.MESSAGE_BROKER_URL.replace("kafka://", "")
            self.producer = aiokafka.AIOKafkaProducer(
                bootstrap_servers=broker_url
            )
            await self.producer.start()
            self.connected = True
            logger.info("Connected to Kafka broker")
        except Exception as e:
            logger.error(f"Failed to connect to Kafka broker: {e}")
            self.connected = False
    
    async def disconnect(self) -> None:
        """
        Disconnect from Kafka broker
        """
        if self.producer and self.connected:
            await self.producer.stop()
            self.connected = False
            logger.info("Disconnected from Kafka broker")
    
    async def publish_event(self, topic: str, event_data: Dict[str, Any]) -> bool:
        """
        Publish an event to Kafka
        """
        if not self.connected:
            await self.connect()
            if not self.connected:
                return False
        
        try:
            value = json.dumps(event_data).encode("utf-8")
            await self.producer.send_and_wait(topic, value)
            logger.info(f"Event published to {topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False
    
    async def publish_password_reset_requested(self, user_data: Dict[str, Any]) -> bool:
        """
        Publish a password reset requested event
        """
        topic = "user_events"
        event = {
            "event_type": "password_reset_requested",
            "data": {
                "user_id": str(user_data["id"]),
                "email": user_data["email"],
                "requested_at": str(user_data["requested_at"]),
            }
        }
        return await self.publish_event(topic, event)
    
    async def publish_password_reset_completed(self, user_data: Dict[str, Any]) -> bool:
        """
        Publish a password reset completed event
        """
        topic = "user_events"
        event = {
            "event_type": "password_reset_completed",
            "data": {
                "user_id": str(user_data["id"]),
                "email": user_data["email"],
                "reset_at": str(user_data["reset_at"]),
            }
        }
        return await self.publish_event(topic, event)


# Singleton instance
event_publisher = EventPublisher()
