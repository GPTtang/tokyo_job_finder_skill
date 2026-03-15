from job_finder.autofilters import (
    apply_dynamic_filters_to_sources,
    build_provider_filters_from_profile,
    merge_provider_filters,
)


def test_build_provider_filters_from_profile():
    profile = {
        "target_roles": ["AI Engineer"],
        "locations": ["Tokyo", "Remote"],
        "skills": ["Python", "RAG"],
        "keyword_terms": ["FastAPI"],
        "remote_preference": "prefer",
    }
    filters = build_provider_filters_from_profile(profile)
    assert "AI Engineer" in filters["keywords"]
    assert "Python" in filters["keywords"]
    assert "Tokyo" in filters["locations"]
    assert filters["remote_preferred"] is True


def test_merge_provider_filters():
    static = {"keywords": ["LLM"], "locations": ["Japan"], "remote_preferred": True}
    dynamic = {"keywords": ["Python"], "locations": ["Tokyo"], "remote_preferred": True}
    merged = merge_provider_filters(static, dynamic)
    assert "LLM" in merged["keywords"]
    assert "Python" in merged["keywords"]
    assert "Japan" in merged["locations"]
    assert "Tokyo" in merged["locations"]
    assert merged["remote_preferred"] is True


def test_apply_dynamic_filters_to_sources():
    sources = [{"provider": "greenhouse", "token": "openai"}]
    profile = {
        "target_roles": ["LLM Engineer"],
        "locations": ["Tokyo"],
        "skills": ["Python"],
        "keyword_terms": [],
        "remote_preference": None,
    }
    out = apply_dynamic_filters_to_sources(sources, profile)
    assert out[0]["filters"]["locations"] == ["Tokyo"]
    assert "LLM Engineer" in out[0]["filters"]["keywords"]
