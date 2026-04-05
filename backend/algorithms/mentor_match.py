"""
Algorithm 2: Mentor Match Score

MentorMatch(U, M) = a1*F + a2*G + a3*R + a4*Lang + a5*C + a6*Q + a7*X

F    = field alignment         | user skills/interests vs mentor expertise
G    = goal alignment          | user goals vs mentor field
R    = regional/cultural       | same country or diaspora from user's country
Lang = language compatibility  | shared language
C    = mentor capacity         | has slots available
Q    = mentor quality          | rating-based score
X    = experience alignment    | experience_years normalised
"""
from __future__ import annotations

from backend.config import settings
from backend.models.mentor import Mentor
from backend.models.user import User


def _field_alignment(user: User, mentor: Mentor) -> float:
    user_tags = {t.lower() for t in user.interests + user.skills}
    mentor_tags = {t.lower() for t in mentor.expertise_tags + [mentor.field.lower()]}
    if not mentor_tags:
        return 0.0
    intersection = len(user_tags & mentor_tags)
    union = len(user_tags | mentor_tags)
    return intersection / union if union else 0.0


def _goal_alignment(user: User, mentor: Mentor) -> float:
    if not user.goals:
        return 0.5
    goals_lower = user.goals.lower()
    field_lower = mentor.field.lower()
    # Check if mentor field keywords appear in user goals
    field_words = field_lower.replace("-", " ").split()
    matches = sum(1 for w in field_words if w in goals_lower)
    return min(matches / max(len(field_words), 1), 1.0)


def _regional_relevance(user: User, mentor: Mentor) -> float:
    if mentor.country.lower() == user.country.lower():
        return 1.0  # same country
    if mentor.diaspora_status:
        # Diaspora mentor: still highly relevant
        return 0.85
    return 0.4


def _language_compatibility(user: User, mentor: Mentor) -> float:
    if user.language.lower() == mentor.language.lower():
        return 1.0
    # Both English-capable is a reasonable fallback
    if "english" in (user.language.lower(), mentor.language.lower()):
        return 0.7
    return 0.3


def _capacity_score(mentor: Mentor) -> float:
    if not mentor.availability:
        return 0.0
    # Normalise: capacity 1 = 0.5, capacity 5+ = 1.0
    return min(mentor.mentorship_capacity / 5.0, 1.0)


def _quality_score(mentor: Mentor) -> float:
    # Rating is 1–10; normalise to 0–1
    return mentor.rating / 10.0


def _experience_score(mentor: Mentor) -> float:
    # Normalise experience: 0yrs=0, 10+yrs=1
    return min(mentor.experience_years / 10.0, 1.0)


def mentor_match_score(user: User, mentor: Mentor) -> float:
    """Returns a score in [0, 1] for mentor-user fit."""
    s = settings
    score = (
        s.a_field      * _field_alignment(user, mentor)
        + s.a_goal     * _goal_alignment(user, mentor)
        + s.a_region   * _regional_relevance(user, mentor)
        + s.a_language * _language_compatibility(user, mentor)
        + s.a_capacity * _capacity_score(mentor)
        + s.a_quality  * _quality_score(mentor)
        + s.a_experience * _experience_score(mentor)
    )
    return round(min(score, 1.0), 4)


def mentor_match_reasons(user: User, mentor: Mentor) -> list[str]:
    reasons: list[str] = []
    if _field_alignment(user, mentor) > 0.3:
        reasons.append(f"Strong field overlap with your interests")
    if _regional_relevance(user, mentor) >= 0.85:
        if mentor.diaspora_status:
            reasons.append("Diaspora mentor — understands your regional context")
        else:
            reasons.append("Based in your country")
    if _language_compatibility(user, mentor) == 1.0:
        reasons.append(f"Speaks {mentor.language}")
    if mentor.experience_years >= 5:
        reasons.append(f"{mentor.experience_years} years of experience")
    if mentor.rating >= 8.0:
        reasons.append(f"Highly rated ({mentor.rating}/10)")
    return reasons
