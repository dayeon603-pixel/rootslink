from fastapi import APIRouter, Depends, HTTPException, status
from loguru import logger
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered.")

    user = User(
        name=payload.name,
        email=payload.email,
        country=payload.country,
        region=payload.region,
        language=payload.language,
        goals=payload.goals,
        education_level=payload.education_level,
        mobility_intent=payload.mobility_intent,
    )
    user.interests = payload.interests
    user.skills = payload.skills
    user.barriers = payload.barriers

    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"New user registered: id={user.id}, country={user.country}")
    return user


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserRead:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user


@router.get("/", response_model=list[UserRead])
def list_users(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)) -> list[UserRead]:
    return db.query(User).offset(skip).limit(limit).all()


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)) -> UserRead:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user
