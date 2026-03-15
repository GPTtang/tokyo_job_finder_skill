from job_finder.config import validate_config


def test_validate_config_filters_ok():
    errors, warnings = validate_config({
        "sources": [
            {
                "provider": "greenhouse",
                "token": "openai",
                "filters": {
                    "keywords": ["AI", "LLM"],
                    "locations": ["Tokyo"],
                    "remote_preferred": True,
                }
            }
        ]
    })
    assert errors == []
