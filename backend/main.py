from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend.config import settings
from backend.database import init_db
from backend.routers import matching, mentors, opportunities, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} v{settings.version}")
    init_db()
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description=(
        "RootsLink API — talent retention matching platform. "
        "Connects students with mentors and opportunities using "
        "OpportunityFit, MentorMatch, BrainDrainRisk, and RetentionPriority algorithms."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(mentors.router)
app.include_router(opportunities.router)
app.include_router(matching.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "version": settings.version}


@app.get("/info")
def info() -> dict:
    return {
        "name": settings.app_name,
        "version": settings.version,
        "algorithms": [
            "OpportunityFit",
            "MentorMatch",
            "BrainDrainRisk",
            "RetentionPriority",
        ],
        "docs": "/docs",
    }
