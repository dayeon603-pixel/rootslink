from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "RootsLink API"
    version: str = "0.1.0"
    database_url: str = "sqlite:///./rootslink.db"
    debug: bool = True

    # Algorithm weights — OpportunityFit
    w_skill: float = 0.20
    w_interest: float = 0.20
    w_eligibility: float = 0.20
    w_location: float = 0.15
    w_aspiration: float = 0.10
    w_barrier: float = 0.10
    w_timing: float = 0.05

    # Algorithm weights — MentorMatch
    a_field: float = 0.25
    a_goal: float = 0.20
    a_region: float = 0.15
    a_language: float = 0.15
    a_capacity: float = 0.10
    a_quality: float = 0.10
    a_experience: float = 0.05

    # Algorithm weights — BrainDrainRisk
    b_mismatch: float = 0.20
    b_mentorship_scarcity: float = 0.15
    b_financial: float = 0.15
    b_digital: float = 0.10
    b_disengagement: float = 0.10
    b_community: float = 0.10
    b_opportunity_desert: float = 0.10
    b_visibility: float = 0.10  # subtracted

    # Algorithm weights — RetentionPriority
    c_growth: float = 0.20
    c_regional: float = 0.20
    c_knowledge_return: float = 0.15
    c_network: float = 0.15
    c_contribution: float = 0.15
    c_local_continuation: float = 0.10
    c_user_preference: float = 0.05

    # Final recommendation blend
    alpha: float = 0.35   # OpportunityFit
    beta: float = 0.25    # MentorSupport
    gamma: float = 0.25   # RetentionPriority
    delta: float = 0.15   # BrainDrainRisk penalty

    class Config:
        env_file = ".env"


settings = Settings()
