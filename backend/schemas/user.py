from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr
    country: str = Field(..., min_length=1, max_length=80)
    region: str | None = None
    language: str = "English"
    interests: list[str] = []
    skills: list[str] = []
    barriers: list[str] = []
    goals: str | None = None
    education_level: str | None = None
    mobility_intent: float = Field(default=0.5, ge=0.0, le=1.0)


class UserRead(UserCreate):
    id: int
    retention_score: float
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    name: str | None = None
    region: str | None = None
    language: str | None = None
    interests: list[str] | None = None
    skills: list[str] | None = None
    barriers: list[str] | None = None
    goals: str | None = None
    education_level: str | None = None
    mobility_intent: float | None = Field(default=None, ge=0.0, le=1.0)
