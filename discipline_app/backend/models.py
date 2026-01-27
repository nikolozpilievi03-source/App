from pydantic import BaseModel, field_serializer
from datetime import date, time
from typing import Optional


class Routine(BaseModel):
    id: Optional[int] = None
    title: str
    routine_date: date
    routine_time: time  # Pydantic automatically converts "15:29" to a time object
    status: str = "pending"
    reminder_sent: bool = False
    streak: int = 0
    failures: int = 0
    personality: str = "hood"
    reminder_minutes_before: int = 10
    grace_minutes_after: int = 5

    @field_serializer('routine_time')
    def serialize_time(self, t: time, _info):
        """Serialize time as HH:MM format (no seconds, no timezone)"""
        return t.strftime('%H:%M')

    @field_serializer('routine_date')
    def serialize_date(self, d: date, _info):
        """Serialize date as YYYY-MM-DD format"""
        return d.strftime('%Y-%m-%d')