from datetime import datetime

from pydantic import BaseModel, model_validator, Field, ValidationError


class Task(BaseModel):
    id: int
    title: str
    frequency_hours: int | None = Field(gt=0, default=None)
    delayed_until: datetime | None
    remind_after: datetime
