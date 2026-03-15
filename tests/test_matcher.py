from job_finder.fetchers import seed_jobs
from job_finder.matcher import rank_jobs
from job_finder.parsers import parse_user_query


def test_rank_jobs_returns_results():
    profile = parse_user_query(
        "I want AI Engineer jobs in Tokyo. I know Python, RAG, FastAPI, Agent."
    )
    jobs = seed_jobs()
    ranked = rank_jobs(profile, jobs, top_n=3)

    assert len(ranked) == 3
    assert ranked[0].match_score >= ranked[-1].match_score
