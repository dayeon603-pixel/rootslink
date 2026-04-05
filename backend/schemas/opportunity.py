from datetime import date, datetime

from pydantic import BaseModel, Field


class OpportunityCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    organization: str = Field(..., min_length=1, max_length=200)
    type: str  # scholarship/internship/fellowship/competition/research/hackathon
    mode: str  # local/remote/hybrid/international
    region: str | None = None
    country: str | None = None
    field_tags: list[str] = []
    language_requirements: list[str] = ["English"]
    eligibility_rules: dict = {}
    description: str | None = None
    deadline: date | None = None
    cost: float = Field(default=0.0, ge=0.0)
    impact_score: float = Field(default=5.0, ge=1.0, le=10.0)
    link: str | None = None


class OpportunityRead(OpportunityCreate):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class OpportunityFilter(BaseModel):
    type: str | None = None
    mode: str | None = None
    region: str | None = None
    field_tag: str | None = None
    max_cost: float | None = None
    language: str | None = None
