from job_finder.fetchers import FetchIssue, FetchResult


def test_fetch_result_ok_property():
    result = FetchResult(provider="demo", jobs=[{"title": "AI Engineer"}], issues=[])
    assert result.ok is True

    result = FetchResult(
        provider="demo",
        jobs=[{"title": "AI Engineer"}],
        issues=[FetchIssue(provider="demo", message="boom", severity="error")],
    )
    assert result.ok is False
