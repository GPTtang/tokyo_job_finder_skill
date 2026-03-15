from __future__ import annotations

from typing import Dict, List


class MatchRecord(dict):
    """Dictionary-backed record that also exposes attribute access."""

    def __getattr__(self, key: str):  # pragma: no cover - trivial helper
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key: str, value):  # pragma: no cover - trivial helper
        self[key] = value

    def copy(self):  # pragma: no cover - keep dict semantics when copied
        return MatchRecord(self)


def _overlap(a: List[str], b: List[str]) -> float:
    if not a or not b:
        return 0.0
    sa = {x.lower() for x in a}
    sb = {x.lower() for x in b}
    return len(sa & sb) / max(len(sa), 1)


def score_job(profile: Dict[str, object], job: Dict[str, object]) -> Dict[str, object]:
    title = str(job.get("title", ""))
    location = str(job.get("location", ""))
    description = str(job.get("description", ""))

    target_roles = profile.get("target_roles", []) or []
    target_locations = profile.get("locations", []) or []
    target_skills = profile.get("skills", []) or []

    title_match = 0.0
    if target_roles:
        title_l = title.lower()
        title_match = max(1.0 if role.lower() in title_l else 0.0 for role in target_roles)

    location_match = 0.0
    if target_locations:
        loc_l = location.lower()
        location_match = max(1.0 if loc.lower() in loc_l else 0.0 for loc in target_locations)

    skill_match = _overlap(target_skills, job.get("skills", []) or [])
    match_score = round(0.5 * skill_match + 0.3 * title_match + 0.2 * location_match, 3)

    reasons = []
    gaps = []

    for skill in target_skills:
        if skill.lower() in {s.lower() for s in (job.get("skills", []) or [])}:
            reasons.append(f"技能命中：{skill}")

    if target_roles and title_match > 0:
        reasons.append("职位标题与目标方向接近")
    if target_locations and location_match > 0:
        reasons.append("地点偏好匹配")

    job_text = f"{title} {description}".lower()
    for maybe_gap in ["AWS", "Kubernetes", "Japanese", "Go", "React"]:
        if maybe_gap.lower() in job_text and maybe_gap.lower() not in {s.lower() for s in target_skills}:
            gaps.append(maybe_gap)

    enriched = MatchRecord(job)
    enriched["match_score"] = match_score
    enriched["fit_reasons"] = reasons[:4]
    enriched["gaps"] = gaps[:4]
    return enriched


def rank_jobs(profile: Dict[str, object], jobs: List[Dict[str, object]], top_n: int = 5) -> List[Dict[str, object]]:
    ranked = [score_job(profile, job) for job in jobs]
    ranked.sort(key=lambda x: (x.get("match_score", 0), x.get("company", ""), x.get("title", "")), reverse=True)
    return ranked[:top_n]
