"""
Matching Service — orchestrates all 4 algorithms into a unified recommendation pipeline.

Pipeline:
  1. Filter out ineligible opportunities (hard rules)
  2. Score all passing opportunities with OpportunityFit + RetentionPriority
  3. Score all available mentors with MentorMatch
  4. Compute BrainDrainRisk for the user
  5. Compute FinalScore = α*OpportunityFit + γ*RetentionPriority (opportunity ranking)
  6. Build pathway summary
  7. Return MatchResult
"""
from __future__ import annotations

from datetime import date

from loguru import logger
from sqlalchemy.orm import Session

from backend.algorithms.brain_drain_risk import brain_drain_risk_score, risk_level
from backend.algorithms.mentor_match import mentor_match_reasons, mentor_match_score
from backend.algorithms.opportunity_fit import opportunity_fit_score, score_reasons
from backend.algorithms.retention_priority import retention_priority_score
from backend.config import settings
from backend.models.mentor import Mentor
from backend.models.opportunity import Opportunity
from backend.models.user import User
from backend.schemas.matching import MatchResult, ScoredMentor, ScoredOpportunity

TOP_N_OPPORTUNITIES = 5
TOP_N_MENTORS = 3


def _is_eligible(user: User, opp: Opportunity) -> bool:
    """Hard filter: remove expired, too-expensive, and language-incompatible opportunities."""
    if opp.deadline and opp.deadline < date.today():
        return False
    rules = opp.eligibility_rules
    max_cost = rules.get("max_cost")
    if max_cost is not None and opp.cost > max_cost and "financial" in user.barriers:
        return False
    return True


def _build_pathway_summary(
    user: User,
    top_opps: list[ScoredOpportunity],
    top_mentors: list[ScoredMentor],
    risk: float,
) -> list[str]:
    steps: list[str] = []

    if top_mentors:
        steps.append(f"Step 1 — Connect with a mentor: {top_mentors[0].name} ({top_mentors[0].field})")
    else:
        steps.append("Step 1 — No mentors matched yet. Join the network to expand the mentor pool.")

    if top_opps:
        immediate = [o for o in top_opps if o.mode in ("remote", "local")]
        if immediate:
            steps.append(f"Step 2 — Apply now: {immediate[0].title} ({immediate[0].organization})")

    if len(top_opps) > 1:
        steps.append(f"Step 3 — Build skills via: {top_opps[1].title}")

    if risk >= 0.65:
        steps.append(
            "Step 4 — High brain-drain risk detected. Prioritise local/regional opportunities "
            "and connect with diaspora mentors to strengthen local pathways."
        )
    else:
        steps.append("Step 4 — Explore regional competitions or fellowships to build your network.")

    steps.append("Step 5 — Track your applications and update your profile as your skills grow.")
    return steps


def generate_matches(user: User, db: Session) -> MatchResult:
    logger.info(f"Generating matches for user_id={user.id}")

    all_opportunities: list[Opportunity] = db.query(Opportunity).all()
    all_mentors: list[Mentor] = db.query(Mentor).filter(Mentor.availability == True).all()  # noqa: E712

    # — Opportunities —
    eligible_opps = [o for o in all_opportunities if _is_eligible(user, o)]
    logger.debug(f"{len(eligible_opps)}/{len(all_opportunities)} opportunities passed eligibility filter")

    scored_opps: list[ScoredOpportunity] = []
    for opp in eligible_opps:
        fit = opportunity_fit_score(user, opp)
        retention = retention_priority_score(user, opp)
        final = settings.alpha * fit + settings.gamma * retention
        reasons, barriers = score_reasons(user, opp)
        scored_opps.append(
            ScoredOpportunity(
                opportunity_id=opp.id,
                title=opp.title,
                organization=opp.organization,
                type=opp.type,
                mode=opp.mode,
                opportunity_fit_score=fit,
                retention_priority_score=retention,
                final_score=round(final, 4),
                reasons=reasons,
                barriers=barriers,
                link=opp.link,
            )
        )

    scored_opps.sort(key=lambda x: x.final_score, reverse=True)
    top_opps = scored_opps[:TOP_N_OPPORTUNITIES]

    # — Mentors —
    scored_mentors: list[ScoredMentor] = []
    for mentor in all_mentors:
        score = mentor_match_score(user, mentor)
        reasons = mentor_match_reasons(user, mentor)
        scored_mentors.append(
            ScoredMentor(
                mentor_id=mentor.id,
                name=mentor.name,
                field=mentor.field,
                country=mentor.country,
                language=mentor.language,
                diaspora_status=mentor.diaspora_status,
                mentor_match_score=score,
                reasons=reasons,
            )
        )

    scored_mentors.sort(key=lambda x: x.mentor_match_score, reverse=True)
    top_mentors = scored_mentors[:TOP_N_MENTORS]

    # — Brain-Drain Risk —
    risk = brain_drain_risk_score(user, mentor_count=len(scored_mentors))
    level = risk_level(risk)

    # — Pathway —
    pathway = _build_pathway_summary(user, top_opps, top_mentors, risk)

    logger.info(
        f"user_id={user.id} | risk={risk} ({level}) | "
        f"top_opp={top_opps[0].title if top_opps else 'none'}"
    )

    return MatchResult(
        user_id=user.id,
        brain_drain_risk=risk,
        risk_level=level,
        top_opportunities=top_opps,
        top_mentors=top_mentors,
        pathway_summary=pathway,
    )
