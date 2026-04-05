from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from loguru import logger

from backend.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # SQLite only
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from backend.models import user, mentor, opportunity, interaction  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created.")
