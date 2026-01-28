from pydantic import BaseModel, field_serializer
from datetime import date, time
from typing import Optional

class Routine(BaseModel):
    id: Optional[int] = None
    title: str
    routine_date: date
    routine_time: time
    status: str = "pending"
    reminder_sent: bool = False
    streak: int = 0
    failures: int = 0
    personality: str = "hood"
    reminder_minutes_before: int = 10
    grace_minutes_after: int = 5
    user_id: Optional[str] = "default"  # ADD THIS LINE
    
    @field_serializer('routine_time')
    def serialize_time(self, t: time, _info):
        return t.strftime('%H:%M')
    
    @field_serializer('routine_date')
    def serialize_date(self, d: date, _info):
        return d.strftime('%Y-%m-%d')