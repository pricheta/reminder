from datetime import datetime

from pydantic import BaseModel


class Task(BaseModel):
    id: int
    title: str
    description: str | None = None
    frequency_hours: int
    next_time_to_do: datetime
