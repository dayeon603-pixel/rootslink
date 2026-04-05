"""
Algorithm 4: Local Retention Priority Score

RetentionPriority(U, O) = c1*G + c2*R + c3*K + c4*N + c5*C + c6*L + c7*Y

G = growth potential          | opportunity impact_score
R = regional relevance        | opportunity is local or regional
K = knowledge return          | opportunity encourages staying/returning
N = community network effect  | type likely to build local connections
C = contribution potential    | opportunity leads to local output
L = local continuation        | opportunity is not purely extractive
Y = user preference weight    | user prefers local (low mobility_intent)

Higher score = this opportunity is better for talent retention.
"""
from __future__ import annotations

from backend.config import settings
from backend.models.opportunity import Opportunity
from backend.models.user import User

# Types that tend to build local networks
COMMUNITY_TYPES: set[str] = {"fellowship", "competition", "hackathon", "research", "internship"}

# Types with high knowledge-return potential
KNOWLEDGE_RETURN_TYPES: set[str] = {"research", "fellowship", "scholarship"}

# Modes that keep users locally connected
LOCAL_MODES: set[str] = {"local", "hybrid"}


def _growth_potential(opp: Opportunity) -> float:
    return opp.impact_score / 10.0


def _regional_relevance(user: User, opp: Opportunity) -> float:
    if opp.mode in LOCAL_MODES:
        if opp.country and opp.country.lower() == user.country.lower():
            return 1.0
        if opp.region and opp.region.lower() == (user.region or "").lower():
            return 0.9
        return 0.5
    if opp.mode == "remote":
        return 0.7  # remote still keeps user physically local
    return 0.3  # international/extractive


def _knowledge_return(opp: Opportunity) -> float:
    if opp.type.lower() in KNOWLEDGE_RETURN_TYPES:
        return 0.9
    if opp.mode == "remote":
        return 0.7
    return 0.4


def _network_effect(opp: Opportunity) -> float:
    if opp.type.lower() in COMMUNITY_TYPES:
        return 0.85
    return 0.4


def _contribution_potential(opp: Opportunity) -> float:
    """Opportunities with high impact_score and local mode = high contribution."""
    base = opp.impact_score / 10.0
    if opp.mode in LOCAL_MODES:
        return min(base * 1.2, 1.0)
    return base * 0.7


def _local_continuation(opp: Opportunity) -> float:
    if opp.mode == "local":
        return 1.0
    if opp.mode in ("remote", "hybrid"):
        return 0.8
    return 0.3  # international = lower local continuation


def _user_preference(user: User) -> float:
    """Users who want to stay locally get higher retention priority weight."""
    return 1.0 - user.mobility_intent


def retention_priority_score(user: User, opp: Opportunity) -> float:
    """Returns a score in [0, 1]. Higher = better for talent retention."""
    s = settings
    score = (
        s.c_growth               * _growth_potential(opp)
        + s.c_regional           * _regional_relevance(user, opp)
        + s.c_knowledge_return   * _knowledge_return(opp)
        + s.c_network            * _network_effect(opp)
        + s.c_contribution       * _contribution_potential(opp)
        + s.c_local_continuation * _local_continuation(opp)
        + s.c_user_preference    * _user_preference(user)
    )
    return round(min(score, 1.0), 4)
