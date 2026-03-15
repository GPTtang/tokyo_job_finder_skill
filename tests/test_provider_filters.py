from job_finder.fetchers import _apply_source_filters


def test_apply_source_filters_keywords_and_remote():
    jobs = [
        {"title": "AI Engineer", "company": "A", "location": "Tokyo", "description": "LLM work", "skills": ["Python"], "remote": True},
        {"title": "Backend Engineer", "company": "B", "location": "Osaka", "description": "APIs", "skills": ["Go"], "remote": False},
    ]
    filtered, issues = _apply_source_filters(
        jobs,
        {"keywords": ["LLM"], "remote_only": True},
        provider="greenhouse",
    )
    assert len(filtered) == 1
    assert filtered[0]["company"] == "A"
