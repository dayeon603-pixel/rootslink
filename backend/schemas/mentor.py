from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class MentorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    field: str = Field(..., min_length=1, max_length=120)
    country: str = Field(..., min_length=1, max_length=80)
    language: str = "English"
    diaspora_status: bool = False
    experience_years: int = Field(default=0, ge=0)
    mentorship_capacity: int = Field(default=3, ge=1, le=20)
    availability: bool = True
    expertise_tags: list[str] = []
    bio: str | None = None


class MentorRead(MentorCreate):
    id: int
    rating: float
    created_at: datetime

    model_config = {"from_attributes": True}


class MentorUpdate(BaseModel):
    field: str | None = None
    language: str | None = None
    diaspora_status: bool | None = None
    experience_years: int | None = Field(default=None, ge=0)
    mentorship_capacity: int | None = Field(default=None, ge=1, le=20)
    availability: bool | None = None
    expertise_tags: list[str] | None = None
    bio: str | None = None
