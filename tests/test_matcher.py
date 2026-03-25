from job_finder.fetchers import seed_jobs
from job_finder.matcher import _detect_jlpt_requirement, rank_jobs, score_job
from job_finder.parsers import parse_user_query


def test_rank_jobs_returns_results():
    profile = parse_user_query(
        "I want AI Engineer jobs in Tokyo. I know Python, RAG, FastAPI, Agent."
    )
    jobs = seed_jobs()
    ranked = rank_jobs(profile, jobs, top_n=3)

    assert len(ranked) == 3
    assert ranked[0].match_score >= ranked[-1].match_score


def test_match_score_never_negative():
    """BUG-5: JLPT penalty must not push match_score below 0."""
    profile = {
        "target_roles": ["Software Engineer"],
        "locations": ["Tokyo"],
        "skills": [],
        "is_chinese_speaker": False,
        "jlpt_level": "N3",
    }
    job = {
        "title": "Software Engineer",
        "location": "Tokyo",
        "description": "Requires N1. Fluent Japanese (N1 level) mandatory.",
        "skills": [],
    }
    result = score_job(profile, job)
    assert result["match_score"] >= 0.0


def test_detect_jlpt_requires_strictest():
    """_detect_jlpt_requirement should return the most stringent level when multiple appear."""
    # Job mentions both N2 and N3 — the real requirement is N2 (strictest)
    text = "ビジネス日本語 (N2) preferred, or at minimum 日常会話 (N3)"
    level = _detect_jlpt_requirement(text)
    assert level == "N2"
