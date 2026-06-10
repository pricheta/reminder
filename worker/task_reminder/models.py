from datetime import datetime

from pydantic import BaseModel, model_validator, Field, ValidationError


class Task(BaseModel):
    id: int
    title: str
    is_repeatable: bool
    frequency_hours: int | None = Field(gt=0, default=None)
    next_time_to_do: datetime

    @model_validator(mode='after')
    def contains_frequency_hours_if_repeatable(self):
        if self. is_repeatable and not self.frequency_hours:
            raise ValidationError('Frequency hours cannot be empty')
