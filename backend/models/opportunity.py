import json
from datetime import date, datetime

from sqlalchemy import Column, Date, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship

from backend.database import Base


class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    organization = Column(String(200), nullable=False)
    type = Column(String(60), nullable=False)  # scholarship/internship/fellowship/competition/research/hackathon
    mode = Column(String(40), nullable=False)  # local/remote/hybrid/international
    region = Column(String(120), nullable=True)  # target region, None = global
    country = Column(String(80), nullable=True)

    _field_tags = Column("field_tags", Text, default="[]")
    _language_requirements = Column("language_requirements", Text, default='["English"]')
    _eligibility_rules = Column("eligibility_rules", Text, default="{}")

    description = Column(Text, nullable=True)
    deadline = Column(Date, nullable=True)
    cost = Column(Float, default=0.0)  # 0 = free
    impact_score = Column(Float, default=5.0)  # 1-10 editorial score
    link = Column(String(500), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def field_tags(self) -> list[str]:
        return json.loads(self._field_tags)

    @field_tags.setter
    def field_tags(self, value: list[str]) -> None:
        self._field_tags = json.dumps(value)

    @property
    def language_requirements(self) -> list[str]:
        return json.loads(self._language_requirements)

    @language_requirements.setter
    def language_requirements(self, value: list[str]) -> None:
        self._language_requirements = json.dumps(value)

    @property
    def eligibility_rules(self) -> dict:
        return json.loads(self._eligibility_rules)

    @eligibility_rules.setter
    def eligibility_rules(self, value: dict) -> None:
        self._eligibility_rules = json.dumps(value)
