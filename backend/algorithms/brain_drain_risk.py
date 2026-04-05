"""
Algorithm 3: Brain-Drain Risk Index

BrainDrainRisk = b1*P + b2*M + b3*F + b4*D + b5*H + b6*C + b7*O - b8*V

P = aspiration-opportunity mismatch  | user ambition vs local availability
M = mentorship scarcity              | no mentor matched yet
F = financial constraint severity    | financial barrier present
D = digital/information access gap   | internet barrier present
H = historical disengagement signals | mobility_intent score
C = community support weakness       | barriers include social/family
O = opportunity desert               | user region has few opportunities
V = visibility of local pathways     | (subtracted) local success visible

Higher score = higher risk of brain drain.
Score is normalised to [0, 1].
"""
from __future__ import annotations

from backend.config import settings
from backend.models.user import User

# Regions with known low opportunity density (MVP approximation)
LOW_OPPORTUNITY_REGIONS: set[str] = {
    "sub-saharan africa", "rural", "remote", "northern africa",
    "central asia", "southeast asia", "pacific islands",
}


def _aspiration_mismatch(user: User) -> float:
    """High ambition + high mobility intent = high mismatch risk."""
    has_goals = 1.0 if user.goals and len(user.goals) > 20 else 0.3
    return has_goals * user.mobility_intent


def _mentorship_scarcity(user: User, mentor_count: int = 0) -> float:
    """No mentors = high scarcity."""
    if mentor_count == 0:
        return 1.0
    return max(0.0, 1.0 - (mentor_count / 5.0))


def _financial_constraint(user: User) -> float:
    return 1.0 if "financial" in user.barriers else 0.0


def _digital_gap(user: User) -> float:
    return 1.0 if "internet" in user.barriers else 0.0


def _disengagement_history(user: User) -> float:
    """Use mobility_intent as a proxy for historical disengagement."""
    return user.mobility_intent


def _community_weakness(user: User) -> float:
    social_barriers = {"social", "family", "isolation", "no role models"}
    user_barriers = {b.lower() for b in user.barriers}
    overlap = len(social_barriers & user_barriers)
    return min(overlap / len(social_barriers), 1.0)


def _opportunity_desert(user: User) -> float:
    region = (user.region or user.country or "").lower()
    for r in LOW_OPPORTUNITY_REGIONS:
        if r in region:
            return 0.9
    return 0.3  # default moderate


def _local_visibility(user: User) -> float:
    """Higher means more visible local pathways — subtracted from risk."""
    # In MVP: approximate by inverting mobility intent
    return 1.0 - user.mobility_intent


def brain_drain_risk_score(user: User, mentor_count: int = 0) -> float:
    """
    Returns brain-drain risk score in [0, 1].
    Higher = higher risk.
    """
    s = settings
    raw = (
        s.b_mismatch             * _aspiration_mismatch(user)
        + s.b_mentorship_scarcity * _mentorship_scarcity(user, mentor_count)
        + s.b_financial           * _financial_constraint(user)
        + s.b_digital             * _digital_gap(user)
        + s.b_disengagement       * _disengagement_history(user)
        + s.b_community           * _community_weakness(user)
        + s.b_opportunity_desert  * _opportunity_desert(user)
        - s.b_visibility          * _local_visibility(user)
    )
    return round(max(0.0, min(raw, 1.0)), 4)


def risk_level(score: float) -> str:
    if score >= 0.65:
        return "high"
    if score >= 0.35:
        return "medium"
    return "low"
