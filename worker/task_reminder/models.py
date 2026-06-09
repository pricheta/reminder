from datetime import datetime

from pydantic import BaseModel


class Task(BaseModel):
    title: str
    description: str | None = None
    frequency_hours: int
    last_time_done: datetime
