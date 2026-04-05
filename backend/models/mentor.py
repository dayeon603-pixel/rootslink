import json
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.database import Base


class Mentor(Base):
    __tablename__ = "mentors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    field = Column(String(120), nullable=False)
    country = Column(String(80), nullable=False)
    language = Column(String(60), nullable=False, default="English")
    diaspora_status = Column(Boolean, default=False)
    experience_years = Column(Integer, default=0)
    mentorship_capacity = Column(Integer, default=3)  # max concurrent mentees
    availability = Column(Boolean, default=True)
    rating = Column(Float, default=5.0)

    _expertise_tags = Column("expertise_tags", Text, default="[]")
    bio = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    interactions = relationship("Interaction", back_populates="mentor")

    @property
    def expertise_tags(self) -> list[str]:
        return json.loads(self._expertise_tags)

    @expertise_tags.setter
    def expertise_tags(self, value: list[str]) -> None:
        self._expertise_tags = json.dumps(value)
