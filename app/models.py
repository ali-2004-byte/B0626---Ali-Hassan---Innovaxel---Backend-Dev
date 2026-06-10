from pydantic import BaseModel, Field, field_validator
from datetime import datetime,timezone

class CreateEventRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    total_seats: int = Field(gt=0, description="Total seats must be greater than 0")
    event_date: datetime

    @field_validator('name', mode='before')
    def name_must_not_be_blank(cls, v):
        if isinstance(v, str):
            v = v.strip()
        if not v:
            raise ValueError('name must not be empty or whitespace')
        return v

    @field_validator('event_date')
    def date_must_be_future(cls, v):
        if v <= datetime.now(timezone.utc):
            raise ValueError('event_date must be in the future')
        return v


class RegisterUserRequest(BaseModel):
    user_name: str = Field(min_length=1, max_length=50)
    event_id: int

    @field_validator('user_name', mode='before')
    def user_name_must_not_be_blank(cls, v):
        if isinstance(v, str):
            v = v.strip()
        if not v:
            raise ValueError('user_name must not be empty or whitespace')
        return v

class EventResponse(BaseModel):
    id: int
    name: str
    event_date: datetime
    total_seats: int
    total_registrations: int
    available_seats: int


class RegistrationResponse(BaseModel):
    id: int
    event_id: int
    user_name: str
    status: str
    registered_at: datetime