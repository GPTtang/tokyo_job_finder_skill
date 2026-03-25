from __future__ import annotations

from typing import Dict, List

# Signals in job text that indicate Chinese speaker is preferred/advantaged
_CHINESE_ADVANTAGE_SIGNALS = [
    "中国語", "chinese", "中文", "mandarin",
    "中国系", "中国人", "华人", "オフショア", "offshore",
    "bridge se", "ブリッジse", "ブリッジエンジニア",
    "大連", "上海", "北京", "深圳", "沈阳",
    "dalian", "shanghai", "beijing", "shenzhen",
]

# Signals that indicate Bridge SE / offshore coordination role
_BRIDGE_SE_SIGNALS = [
    "bridge se", "ブリッジse", "ブリッジエンジニア", "bridge engineer",
    "オフショア", "offshore", "中国語", "対中", "日中",
    "中国拠点", "中国チーム", "中国開発",
]

# JLPT requirement patterns in job text
_JLPT_REQUIREMENT_MAP = {
    "n1": "N1", "jlpt n1": "N1", "日本語n1": "N1", "n1以上": "N1",
    "native japanese": "N1", "日本語ネイティブ": "N1",
    "n2": "N2", "jlpt n2": "N2", "日本語n2": "N2", "n2以上": "N2",
    "ビジネス日本語": "N2", "business japanese": "N2",
    "n3": "N3", "jlpt n3": "N3", "n3以上": "N3",
    "日常会話": "N3", "conversational japanese": "N3",
}

_JLPT_RANK = {"N1": 1, "N2": 2, "N3": 3, None: 99}


class MatchRecord(dict):
    """Dictionary-backed record that also exposes attribute access."""

    def __getattr__(self, key: str):  # pragma: no cover
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key: str, value):  # pragma: no cover
        self[key] = value

    def copy(self):  # pragma: no cover
        return MatchRecord(self)


def _overlap(a: List[str], b: List[str]) -> float:
    if not a or not b:
        return 0.0
    sa = {x.lower() for x in a}
    sb = {x.lower() for x in b}
    return len(sa & sb) / max(len(sa), 1)


def _detect_chinese_advantage(job_text: str) -> bool:
    """Return True if the job description signals Chinese speaker is preferred."""
    t = job_text.lower()
    return any(sig.lower() in t for sig in _CHINESE_ADVANTAGE_SIGNALS)


def _detect_bridge_se(job_text: str) -> bool:
    """Return True if the role involves Bridge SE / offshore coordination."""
    t = job_text.lower()
    return any(sig.lower() in t for sig in _BRIDGE_SE_SIGNALS)


def _detect_jlpt_requirement(job_text: str) -> str | None:
    """Extract the minimum JLPT level required from job text."""
    t = job_text.lower()
    found = []
    for pattern, level in _JLPT_REQUIREMENT_MAP.items():
        if pattern.lower() in t:
            found.append(level)
    if not found:
        return None
    # Return the strictest (most demanding) requirement found so the penalty is
    # applied correctly when a job signals e.g. both N2 and N3 in the same text.
    return min(found, key=lambda x: _JLPT_RANK[x])


def score_job(profile: Dict[str, object], job: Dict[str, object]) -> Dict[str, object]:
    title = str(job.get("title", ""))
    location = str(job.get("location", ""))
    description = str(job.get("description", ""))
    job_text = f"{title} {description}".lower()

    target_roles = profile.get("target_roles", []) or []
    target_locations = profile.get("locations", []) or []
    target_skills = profile.get("skills", []) or []
    is_chinese_speaker = bool(profile.get("is_chinese_speaker", False))
    candidate_jlpt = profile.get("jlpt_level")  # e.g. "N2"

    # ── Base scores ──────────────────────────────────────────────────
    title_match = 0.0
    if target_roles:
        title_l = title.lower()
        title_match = max(1.0 if role.lower() in title_l else 0.0 for role in target_roles)

    location_match = 0.0
    if target_locations:
        loc_l = location.lower()
        location_match = max(1.0 if loc.lower() in loc_l else 0.0 for loc in target_locations)

    skill_match = _overlap(target_skills, job.get("skills", []) or [])

    # ── Bonus: Chinese speaker advantage ─────────────────────────────
    chinese_advantage = _detect_chinese_advantage(job_text)
    chinese_bonus = 0.15 if (is_chinese_speaker and chinese_advantage) else 0.0

    # ── Bonus: Bridge SE role (high value for bilingual candidates) ───
    is_bridge_se = _detect_bridge_se(job_text)
    bridge_bonus = 0.10 if (is_chinese_speaker and is_bridge_se) else 0.0

    # ── Penalty: JLPT requirement exceeds candidate level ────────────
    required_jlpt = _detect_jlpt_requirement(job_text)
    jlpt_penalty = 0.0
    if required_jlpt and candidate_jlpt:
        if _JLPT_RANK[required_jlpt] < _JLPT_RANK[candidate_jlpt]:
            jlpt_penalty = 0.20  # job requires better Japanese than candidate has

    # ── Final score ───────────────────────────────────────────────────
    base = 0.5 * skill_match + 0.3 * title_match + 0.2 * location_match
    match_score = round(max(0.0, min(1.0, base + chinese_bonus + bridge_bonus) - jlpt_penalty), 3)

    # ── Reasons ───────────────────────────────────────────────────────
    reasons = []
    for skill in target_skills:
        if skill.lower() in {s.lower() for s in (job.get("skills", []) or [])}:
            reasons.append(f"技能命中：{skill}")
    if target_roles and title_match > 0:
        reasons.append("职位标题与目标方向接近")
    if target_locations and location_match > 0:
        reasons.append("地点偏好匹配")
    if chinese_advantage and is_chinese_speaker:
        reasons.append("中国語・中文優遇ポジション（加点）")
    if is_bridge_se and is_chinese_speaker:
        reasons.append("Bridge SE / オフショア連携職（加点）")

    # ── Gaps ─────────────────────────────────────────────────────────
    gaps = []
    candidate_skills_l = {s.lower() for s in target_skills}
    for maybe_gap in ["AWS", "Kubernetes", "Go", "React", "SAP", "COBOL"]:
        if maybe_gap.lower() in job_text and maybe_gap.lower() not in candidate_skills_l:
            gaps.append(maybe_gap)
    if required_jlpt and jlpt_penalty > 0:
        gaps.append(f"日本語要件：{required_jlpt}（現状より高い可能性）")

    enriched = MatchRecord(job)
    enriched["match_score"] = match_score
    enriched["fit_reasons"] = reasons[:5]
    enriched["gaps"] = gaps[:4]
    enriched["chinese_advantage"] = chinese_advantage
    enriched["is_bridge_se"] = is_bridge_se
    enriched["required_jlpt"] = required_jlpt
    return enriched


def rank_jobs(
    profile: Dict[str, object],
    jobs: List[Dict[str, object]],
    top_n: int = 5,
) -> List[Dict[str, object]]:
    ranked = [score_job(profile, job) for job in jobs]
    ranked.sort(
        key=lambda x: (x.get("match_score", 0), x.get("company", ""), x.get("title", "")),
        reverse=True,
    )
    return ranked[:top_n]
