import json
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    country = Column(String(80), nullable=False)
    region = Column(String(120), nullable=True)
    language = Column(String(60), nullable=False, default="English")

    # Stored as JSON strings for SQLite MVP
    _interests = Column("interests", Text, default="[]")
    _skills = Column("skills", Text, default="[]")
    _barriers = Column("barriers", Text, default="[]")

    goals = Column(Text, nullable=True)
    education_level = Column(String(60), nullable=True)  # high_school, undergraduate, graduate
    mobility_intent = Column(Float, default=0.5)  # 0=stay, 1=leave
    retention_score = Column(Float, default=0.5)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    interactions = relationship("Interaction", back_populates="user")

    @property
    def interests(self) -> list[str]:
        return json.loads(self._interests)

    @interests.setter
    def interests(self, value: list[str]) -> None:
        self._interests = json.dumps(value)

    @property
    def skills(self) -> list[str]:
        return json.loads(self._skills)

    @skills.setter
    def skills(self, value: list[str]) -> None:
        self._skills = json.dumps(value)

    @property
    def barriers(self) -> list[str]:
        return json.loads(self._barriers)

    @barriers.setter
    def barriers(self, value: list[str]) -> None:
        self._barriers = json.dumps(value)
