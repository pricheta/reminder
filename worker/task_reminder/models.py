from datetime import datetime

from pydantic import BaseModel, model_validator, Field, ValidationError


class Task(BaseModel):
    id: int
    title: str
    frequency_hours: int | None = Field(gt=0, default=None)
    next_time_to_do: datetime
