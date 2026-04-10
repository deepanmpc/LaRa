import logging
from enum import Enum, auto
from threading import Lock
from typing import Callable, Dict, List, Any

class EventType(Enum):
    SESSION_STARTED = auto()
    TURN_COMPLETED = auto()
    VISION_UPDATE = auto()
    EMOTION_UPDATE = auto()
    LEARNING_UPDATE = auto()
    SESSION_COMPLETED = auto()
    ENGAGEMENT_MINUTE_SYNC = auto()

class EventBus:
    _instance = None
    _lock = Lock()

    def __init__(self):
        if EventBus._instance is not None:
            raise RuntimeError("EventBus is a singleton. Use get()")
        self._subscribers: Dict[EventType, List[Callable]] = {etype: [] for etype in EventType}
        self._sub_lock = Lock()

    @classmethod
    def get(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = EventBus()
        return cls._instance

    def subscribe(self, event_type: EventType, callback: Callable[[Any], None]):
        """Register a callback for a specific event type."""
        with self._sub_lock:
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
                logging.debug(f"[EventBus] Subscribed {callback.__name__} to {event_type.name}")

    def publish(self, event_type: EventType, data: Any = None):
        """Notify all subscribers of an event."""
        logging.info(f"[EventBus] Publishing {event_type.name}")
        with self._sub_lock:
            callbacks = self._subscribers[event_type][:]
        
        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                logging.error(f"[EventBus] Error in callback {callback.__name__} for {event_type.name}: {e}")

    def unsubscribe(self, event_type: EventType, callback: Callable[[Any], None]):
        """Remove a callback for a specific event type."""
        with self._sub_lock:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                logging.debug(f"[EventBus] Unsubscribed {callback.__name__} from {event_type.name}")
