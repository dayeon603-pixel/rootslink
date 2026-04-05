"""
Algorithm 1: User–Opportunity Fit Score

OpportunityFit(U, O) = w1*S + w2*I + w3*E + w4*L + w5*A + w6*B + w7*T

S = skill match          | how well user skills overlap with opportunity field tags
I = interest alignment   | overlap between user interests and opportunity field tags
E = eligibility          | binary: user meets hard requirements (age, education, cost)
L = location feasibility | mode compatibility + region match
A = aspiration alignment | opportunity type matches user goals
B = barrier compatibility | opportunity does not worsen user's known barriers
T = timing readiness     | deadline is not too close or already passed
"""
from __future__ import annotations

from datetime import date

from backend.config import settings
from backend.models.opportunity import Opportunity
from backend.models.user import User


def _tag_overlap(user_tags: list[str], opp_tags: list[str]) -> float:
    """Jaccard-style overlap score between two tag lists."""
    if not opp_tags:
        return 0.5  # neutral if opportunity has no tags
    u = {t.lower() for t in user_tags}
    o = {t.lower() for t in opp_tags}
    if not u:
        return 0.0
    intersection = len(u & o)
    union = len(u | o)
    return intersection / union if union else 0.0


def _skill_match(user: User, opp: Opportunity) -> float:
    return _tag_overlap(user.skills, opp.field_tags)


def _interest_alignment(user: User, opp: Opportunity) -> float:
    return _tag_overlap(user.interests, opp.field_tags)


def _eligibility(user: User, opp: Opportunity) -> float:
    """Returns 1.0 if user passes hard eligibility rules, 0.0 if failed."""
    rules: dict = opp.eligibility_rules

    # Cost check
    max_cost = rules.get("max_cost")
    if max_cost is not None and opp.cost > max_cost:
        if "financial" in user.barriers:
            return 0.0

    # Education level check
    required_edu = rules.get("education_level")
    edu_rank = {"high_school": 1, "undergraduate": 2, "graduate": 3, "phd": 4}
    if required_edu and user.education_level:
        if edu_rank.get(user.education_level, 0) < edu_rank.get(required_edu, 0):
            return 0.0

    return 1.0


def _location_feasibility(user: User, opp: Opportunity) -> float:
    if opp.mode == "remote":
        return 1.0
    if opp.mode == "international":
        # penalise if user has travel/financial barriers
        if any(b in user.barriers for b in ("financial", "transportation")):
            return 0.4
        return 0.9
    if opp.mode == "local":
        # reward exact country match
        if opp.country and opp.country.lower() == user.country.lower():
            return 1.0
        if opp.region and opp.region.lower() == (user.region or "").lower():
            return 0.85
        return 0.3
    # hybrid
    return 0.7


def _aspiration_alignment(user: User, opp: Opportunity) -> float:
    if not user.goals:
        return 0.5
    goals_lower = user.goals.lower()
    type_keywords: dict[str, list[str]] = {
        "scholarship": ["study", "degree", "university", "academic"],
        "internship": ["work", "industry", "experience", "career"],
        "research": ["research", "science", "publish", "lab"],
        "fellowship": ["leadership", "policy", "impact", "fellowship"],
        "competition": ["compete", "win", "hackathon", "challenge"],
        "hackathon": ["build", "tech", "code", "product"],
    }
    keywords = type_keywords.get(opp.type.lower(), [])
    if not keywords:
        return 0.5
    matches = sum(1 for kw in keywords if kw in goals_lower)
    return min(matches / len(keywords), 1.0)


def _barrier_compatibility(user: User, opp: Opportunity) -> float:
    """Score = 1 if opportunity does not conflict with barriers, lower if it does."""
    barriers = set(user.barriers)
    penalty = 0.0

    if "language" in barriers:
        user_lang = user.language.lower()
        opp_langs = [l.lower() for l in opp.language_requirements]
        if opp_langs and user_lang not in opp_langs:
            penalty += 0.4

    if "financial" in barriers and opp.cost > 0:
        penalty += 0.3

    if "internet" in barriers and opp.mode == "remote":
        penalty += 0.3

    return max(0.0, 1.0 - penalty)


def _timing_readiness(opp: Opportunity) -> float:
    if opp.deadline is None:
        return 0.8  # rolling/unknown deadline
    today = date.today()
    days_left = (opp.deadline - today).days
    if days_left < 0:
        return 0.0   # expired
    if days_left < 7:
        return 0.3   # very tight
    if days_left < 21:
        return 0.7
    return 1.0


def opportunity_fit_score(user: User, opp: Opportunity) -> float:
    """
    Returns a score in [0, 1] representing how well this opportunity fits the user.
    """
    s = settings

    score = (
        s.w_skill        * _skill_match(user, opp)
        + s.w_interest   * _interest_alignment(user, opp)
        + s.w_eligibility * _eligibility(user, opp)
        + s.w_location   * _location_feasibility(user, opp)
        + s.w_aspiration * _aspiration_alignment(user, opp)
        + s.w_barrier    * _barrier_compatibility(user, opp)
        + s.w_timing     * _timing_readiness(opp)
    )

    return round(min(score, 1.0), 4)


def score_reasons(user: User, opp: Opportunity) -> tuple[list[str], list[str]]:
    """Returns (positive_reasons, potential_barriers) for explainability."""
    reasons: list[str] = []
    barriers: list[str] = []

    if _skill_match(user, opp) > 0.3:
        reasons.append(f"Matches your skills in {', '.join(opp.field_tags[:2])}")
    if _interest_alignment(user, opp) > 0.3:
        reasons.append("Aligns with your stated interests")
    if opp.mode == "remote":
        reasons.append("Fully remote — accessible from your location")
    if opp.cost == 0:
        reasons.append("Free to apply")
    if _aspiration_alignment(user, opp) > 0.5:
        reasons.append(f"Fits your goals ({opp.type})")

    if _eligibility(user, opp) == 0.0:
        barriers.append("You may not meet eligibility requirements")
    if opp.deadline and (opp.deadline - date.today()).days < 14:
        barriers.append(f"Deadline is soon ({opp.deadline})")
    if opp.cost > 0 and "financial" in user.barriers:
        barriers.append(f"Has a cost (${opp.cost:.0f}) — financial barrier flagged")
    if "language" in user.barriers:
        barriers.append("Language requirements may be a challenge")

    return reasons, barriers
