from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.interaction import Interaction
from backend.models.user import User
from backend.schemas.matching import InteractionCreate, MatchResult
from backend.services.matching_service import generate_matches

router = APIRouter(prefix="/match", tags=["matching"])


@router.get("/{user_id}", response_model=MatchResult)
def match_user(user_id: int, db: Session = Depends(get_db)) -> MatchResult:
    """
    Run the full recommendation pipeline for a user.
    Returns top opportunities, top mentors, brain-drain risk, and a pathway summary.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return generate_matches(user, db)


@router.post("/interaction", status_code=201)
def log_interaction(payload: InteractionCreate, db: Session = Depends(get_db)) -> dict:
    """Log a user interaction (click, apply, feedback) for the feedback learning loop."""
    interaction = Interaction(
        user_id=payload.user_id,
        mentor_id=payload.mentor_id,
        opportunity_id=payload.opportunity_id,
        action=payload.action,
        outcome=payload.outcome,
        notes=payload.notes,
    )
    db.add(interaction)
    db.commit()
    logger.info(f"Interaction logged: user={payload.user_id}, action={payload.action}")
    return {"status": "logged", "action": payload.action}


@router.get("/stats/overview")
def overview_stats(db: Session = Depends(get_db)) -> dict:
    """Basic platform impact counter for the homepage."""
    from backend.models.mentor import Mentor
    from backend.models.opportunity import Opportunity

    users = db.query(User).count()
    mentors = db.query(Mentor).count()
    opportunities = db.query(Opportunity).count()
    interactions = db.query(Interaction).count()

    return {
        "total_users": users,
        "total_mentors": mentors,
        "total_opportunities": opportunities,
        "total_interactions": interactions,
    }
