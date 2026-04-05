from pydantic import BaseModel, Field


class ScoredOpportunity(BaseModel):
    opportunity_id: int
    title: str
    organization: str
    type: str
    mode: str
    opportunity_fit_score: float
    retention_priority_score: float
    final_score: float
    reasons: list[str]
    barriers: list[str]
    link: str | None = None


class ScoredMentor(BaseModel):
    mentor_id: int
    name: str
    field: str
    country: str
    language: str
    diaspora_status: bool
    mentor_match_score: float
    reasons: list[str]


class MatchResult(BaseModel):
    user_id: int
    brain_drain_risk: float
    risk_level: str  # low / medium / high
    top_opportunities: list[ScoredOpportunity]
    top_mentors: list[ScoredMentor]
    pathway_summary: list[str]


class InteractionCreate(BaseModel):
    user_id: int
    mentor_id: int | None = None
    opportunity_id: int | None = None
    action: str  # clicked/saved/applied/meeting_completed/feedback/abandoned
    outcome: str | None = None
    notes: str | None = None
