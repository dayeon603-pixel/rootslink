from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.mentor import Mentor
from backend.schemas.mentor import MentorCreate, MentorRead, MentorUpdate

router = APIRouter(prefix="/mentors", tags=["mentors"])


@router.post("/", response_model=MentorRead, status_code=status.HTTP_201_CREATED)
def register_mentor(payload: MentorCreate, db: Session = Depends(get_db)) -> MentorRead:
    existing = db.query(Mentor).filter(Mentor.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered.")

    mentor = Mentor(
        name=payload.name,
        email=payload.email,
        field=payload.field,
        country=payload.country,
        language=payload.language,
        diaspora_status=payload.diaspora_status,
        experience_years=payload.experience_years,
        mentorship_capacity=payload.mentorship_capacity,
        availability=payload.availability,
        bio=payload.bio,
    )
    mentor.expertise_tags = payload.expertise_tags

    db.add(mentor)
    db.commit()
    db.refresh(mentor)
    logger.info(f"New mentor registered: id={mentor.id}, field={mentor.field}")
    return mentor


@router.get("/{mentor_id}", response_model=MentorRead)
def get_mentor(mentor_id: int, db: Session = Depends(get_db)) -> MentorRead:
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found.")
    return mentor


@router.get("/", response_model=list[MentorRead])
def list_mentors(
    field: str | None = None,
    available_only: bool = True,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[MentorRead]:
    q = db.query(Mentor)
    if available_only:
        q = q.filter(Mentor.availability == True)  # noqa: E712
    if field:
        q = q.filter(Mentor.field.ilike(f"%{field}%"))
    return q.offset(skip).limit(limit).all()


@router.patch("/{mentor_id}", response_model=MentorRead)
def update_mentor(mentor_id: int, payload: MentorUpdate, db: Session = Depends(get_db)) -> MentorRead:
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor not found.")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(mentor, field, value)

    db.commit()
    db.refresh(mentor)
    return mentor
