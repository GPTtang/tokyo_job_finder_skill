from unittest.mock import patch

from job_finder.fetchers import FetchIssue, FetchResult, fetch_lever


def test_fetch_result_ok_property():
    result = FetchResult(provider="demo", jobs=[{"title": "AI Engineer"}], issues=[])
    assert result.ok is True

    # Empty jobs list is NOT a failure (BUG-1 regression)
    result = FetchResult(provider="demo", jobs=[], issues=[])
    assert result.ok is True

    result = FetchResult(
        provider="demo",
        jobs=[{"title": "AI Engineer"}],
        issues=[FetchIssue(provider="demo", message="boom", severity="error")],
    )
    assert result.ok is False


def test_fetch_lever_empty_lists_field():
    """BUG-8: item.get("lists") == [] must not raise IndexError."""
    fake_response = [
        {
            "text": "Software Engineer",
            "categories": {"location": "Tokyo"},
            "descriptionPlain": "Build cool stuff",
            "lists": [],  # empty — previously caused IndexError
            "hostedUrl": "https://lever.co/test/123",
        }
    ]
    with patch("job_finder.fetchers._safe_get_json", return_value=(fake_response, [])):
        result = fetch_lever("testco")
    assert result.ok is True
    assert len(result.jobs) == 1
    assert result.jobs[0]["title"] == "Software Engineer"
