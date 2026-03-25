from job_finder.config import validate_config


def test_validate_config_ok():
    errors, warnings = validate_config({
        "fetch_options": {
            "timeout_seconds": 15,
            "max_retries": 1,
            "retry_backoff_seconds": 0.5,
            "max_follow_links": 3,
        },
        "sources": [
            {"provider": "greenhouse", "token": "openai"},
            {"provider": "lever", "company": "notion"},
        ]
    })
    assert errors == []
    assert isinstance(warnings, list)


def test_validate_config_missing_required_field():
    errors, warnings = validate_config({
        "sources": [
            {"provider": "greenhouse"}
        ]
    })
    assert any("token" in e for e in errors)


def test_validate_config_skips_section_separators():
    """BUG-7: _section/_label objects must not cause validation errors."""
    errors, warnings = validate_config({
        "fetch_options": {
            "timeout_seconds": 15,
            "max_retries": 1,
            "retry_backoff_seconds": 0.5,
            "max_follow_links": 3,
        },
        "sources": [
            {"_section": "Priority 1", "_label": "Japanese big tech"},
            {"provider": "greenhouse", "token": "mercari"},
            {"_section_end": True},
        ]
    })
    assert errors == []
