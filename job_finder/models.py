from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class UserProfile:
    raw_query: str
    target_roles: List[str] = field(default_factory=list)
    locations: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class JobRecord:
    title: str
    company: str
    location: str
    remote: bool
    description: str
    skills: List[str]
    url: str
    source: str
    posted_date: Optional[str] = None
    source_detail: Optional[str] = None


@dataclass
class MatchedJob:
    job: JobRecord
    match_score: float
    title_score: float
    skill_score: float
    location_score: float
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    reasons: List[str] = field(default_factory=list)
