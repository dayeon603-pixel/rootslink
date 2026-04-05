"""
Seed the database with sample mentors, opportunities, and a test user.
Run from project root: python -m data.seed
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import date

from loguru import logger

from backend.database import SessionLocal, init_db
from backend.models.mentor import Mentor
from backend.models.opportunity import Opportunity
from backend.models.user import User


def seed() -> None:
    init_db()
    db = SessionLocal()

    # — Mentors —
    mentors_data = [
        dict(
            name="Amara Diallo", email="amara@example.com", field="Computer Science",
            country="Senegal", language="French", diaspora_status=True,
            experience_years=8, mentorship_capacity=4, availability=True, rating=9.0,
            expertise_tags=["machine learning", "python", "data science"],
            bio="ML engineer based in Paris, originally from Dakar. Passionate about African tech ecosystems.",
        ),
        dict(
            name="Dr. Leila Nazari", email="leila@example.com", field="Public Health",
            country="Iran", language="English", diaspora_status=False,
            experience_years=12, mentorship_capacity=3, availability=True, rating=9.5,
            expertise_tags=["public health", "research", "policy", "global health"],
            bio="WHO consultant with expertise in health systems in developing regions.",
        ),
        dict(
            name="James Okonkwo", email="james@example.com", field="Entrepreneurship",
            country="Nigeria", language="English", diaspora_status=False,
            experience_years=6, mentorship_capacity=5, availability=True, rating=8.5,
            expertise_tags=["startup", "entrepreneurship", "fintech", "product"],
            bio="Founder of two Lagos-based startups. Mentor at multiple African accelerators.",
        ),
        dict(
            name="Sofia Herrera", email="sofia@example.com", field="Environmental Science",
            country="Colombia", language="Spanish", diaspora_status=True,
            experience_years=9, mentorship_capacity=2, availability=True, rating=8.8,
            expertise_tags=["environment", "climate", "research", "SDGs"],
            bio="Environmental researcher at MIT, originally from Bogotá.",
        ),
        dict(
            name="Yuki Tanaka", email="yuki@example.com", field="Engineering",
            country="Japan", language="English", diaspora_status=False,
            experience_years=15, mentorship_capacity=3, availability=True, rating=9.2,
            expertise_tags=["engineering", "robotics", "hardware", "research"],
            bio="Senior engineer at JAXA. Mentors students in STEM across Asia-Pacific.",
        ),
    ]

    for data in mentors_data:
        existing = db.query(Mentor).filter(Mentor.email == data["email"]).first()
        if existing:
            continue
        tags = data.pop("expertise_tags")
        mentor = Mentor(**data)
        mentor.expertise_tags = tags
        db.add(mentor)

    # — Opportunities —
    opportunities_data = [
        dict(
            title="Google Generation Scholarship", organization="Google",
            type="scholarship", mode="international", region=None, country=None,
            field_tags=["computer science", "engineering", "technology"],
            language_requirements=["English"],
            eligibility_rules={"education_level": "undergraduate"},
            description="Scholarship for underrepresented students in CS.",
            deadline=date(2026, 8, 1), cost=0.0, impact_score=9.5,
            link="https://buildyourfuture.withgoogle.com/scholarships",
        ),
        dict(
            title="KCDF Youth Entrepreneurship Grant", organization="Kenya Community Development Foundation",
            type="fellowship", mode="local", region="Sub-Saharan Africa", country="Kenya",
            field_tags=["entrepreneurship", "business", "social impact"],
            language_requirements=["English", "Swahili"],
            eligibility_rules={},
            description="Grant for youth-led social enterprises in Kenya.",
            deadline=date(2026, 7, 15), cost=0.0, impact_score=8.8,
            link="https://kcdf.or.ke",
        ),
        dict(
            title="Coursera Google Data Analytics Certificate", organization="Coursera / Google",
            type="research", mode="remote", region=None, country=None,
            field_tags=["data science", "analytics", "python"],
            language_requirements=["English"],
            eligibility_rules={},
            description="Free professional certificate in data analytics.",
            deadline=None, cost=0.0, impact_score=7.5,
            link="https://coursera.org/professional-certificates/google-data-analytics",
        ),
        dict(
            title="YALI Regional Leadership Center Program", organization="YALI Network",
            type="fellowship", mode="hybrid", region="Sub-Saharan Africa", country=None,
            field_tags=["leadership", "policy", "entrepreneurship", "civic"],
            language_requirements=["English"],
            eligibility_rules={},
            description="Leadership training for young African professionals.",
            deadline=date(2026, 9, 30), cost=0.0, impact_score=9.0,
            link="https://yali.state.gov",
        ),
        dict(
            title="MIT Solve Youth Fellowship", organization="MIT Solve",
            type="fellowship", mode="international", region=None, country=None,
            field_tags=["technology", "social impact", "innovation", "SDGs"],
            language_requirements=["English"],
            eligibility_rules={"education_level": "undergraduate"},
            description="Fellowship for youth-led tech solutions to global challenges.",
            deadline=date(2026, 6, 1), cost=0.0, impact_score=9.8,
            link="https://solve.mit.edu",
        ),
        dict(
            title="Local Hack Day — Seoul", organization="MLH",
            type="hackathon", mode="local", region="East Asia", country="South Korea",
            field_tags=["coding", "hackathon", "product", "technology"],
            language_requirements=["Korean", "English"],
            eligibility_rules={},
            description="One-day local hackathon for student developers.",
            deadline=date(2026, 5, 20), cost=0.0, impact_score=7.0,
            link="https://mlh.io",
        ),
        dict(
            title="Ashoka Young Changemakers", organization="Ashoka",
            type="competition", mode="international", region=None, country=None,
            field_tags=["social impact", "civic", "changemaker", "SDGs"],
            language_requirements=["English"],
            eligibility_rules={},
            description="Global competition for young social innovators.",
            deadline=date(2026, 10, 1), cost=0.0, impact_score=9.3,
            link="https://ashoka.org/young-changemakers",
        ),
        dict(
            title="African Union Youth Volunteer Corps", organization="African Union",
            type="internship", mode="hybrid", region="Sub-Saharan Africa", country=None,
            field_tags=["policy", "governance", "development", "leadership"],
            language_requirements=["English", "French"],
            eligibility_rules={},
            description="Volunteer internship supporting AU development programs.",
            deadline=date(2026, 7, 30), cost=0.0, impact_score=8.5,
            link="https://au.int",
        ),
    ]

    for data in opportunities_data:
        existing = db.query(Opportunity).filter(Opportunity.title == data["title"]).first()
        if existing:
            continue
        tags = data.pop("field_tags")
        lang = data.pop("language_requirements")
        rules = data.pop("eligibility_rules")
        opp = Opportunity(**data)
        opp.field_tags = tags
        opp.language_requirements = lang
        opp.eligibility_rules = rules
        db.add(opp)

    # — Test User —
    test_user_email = "test@rootslink.org"
    if not db.query(User).filter(User.email == test_user_email).first():
        user = User(
            name="Test Student",
            email=test_user_email,
            country="Nigeria",
            region="Lagos",
            language="English",
            goals="I want to study computer science, build tech products, and eventually start a company in Lagos.",
            education_level="undergraduate",
            mobility_intent=0.4,
        )
        user.interests = ["technology", "entrepreneurship", "social impact"]
        user.skills = ["python", "data science", "javascript"]
        user.barriers = ["financial"]
        db.add(user)

    db.commit()
    db.close()
    logger.info("Seed complete.")


if __name__ == "__main__":
    seed()
