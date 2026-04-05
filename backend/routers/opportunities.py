from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.opportunity import Opportunity
from backend.schemas.opportunity import OpportunityCreate, OpportunityRead

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


@router.post("/", response_model=OpportunityRead, status_code=status.HTTP_201_CREATED)
def create_opportunity(payload: OpportunityCreate, db: Session = Depends(get_db)) -> OpportunityRead:
    opp = Opportunity(
        title=payload.title,
        organization=payload.organization,
        type=payload.type,
        mode=payload.mode,
        region=payload.region,
        country=payload.country,
        description=payload.description,
        deadline=payload.deadline,
        cost=payload.cost,
        impact_score=payload.impact_score,
        link=payload.link,
    )
    opp.field_tags = payload.field_tags
    opp.language_requirements = payload.language_requirements
    opp.eligibility_rules = payload.eligibility_rules

    db.add(opp)
    db.commit()
    db.refresh(opp)
    logger.info(f"Opportunity added: id={opp.id}, title={opp.title}")
    return opp


@router.get("/{opportunity_id}", response_model=OpportunityRead)
def get_opportunity(opportunity_id: int, db: Session = Depends(get_db)) -> OpportunityRead:
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    return opp


@router.get("/", response_model=list[OpportunityRead])
def list_opportunities(
    type: str | None = None,
    mode: str | None = None,
    max_cost: float | None = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[OpportunityRead]:
    q = db.query(Opportunity)
    if type:
        q = q.filter(Opportunity.type.ilike(f"%{type}%"))
    if mode:
        q = q.filter(Opportunity.mode == mode)
    if max_cost is not None:
        q = q.filter(Opportunity.cost <= max_cost)
    return q.offset(skip).limit(limit).all()


@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(opportunity_id: int, db: Session = Depends(get_db)) -> None:
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found.")
    db.delete(opp)
    db.commit()
