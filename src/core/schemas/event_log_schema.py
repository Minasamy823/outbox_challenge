from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class EventLogOutboxBaseModel(BaseModel):
    id: int
    event_type: str
    event_date_time: datetime
    destination: str
    event_context: Dict[str, Any]
    metadata_version: int
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True
