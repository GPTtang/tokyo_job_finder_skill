from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List


def build_provider_filters_from_profile(profile: Dict[str, object]) -> Dict[str, Any]:
    keywords: List[str] = []
    locations: List[str] = []

    for role in profile.get("target_roles", []) or []:
        if isinstance(role, str) and role.strip():
            keywords.append(role)

    for skill in profile.get("skills", []) or []:
        if isinstance(skill, str) and skill.strip():
            keywords.append(skill)

    for term in profile.get("keyword_terms", []) or []:
        if isinstance(term, str) and term.strip():
            keywords.append(term)

    for loc in profile.get("locations", []) or []:
        if isinstance(loc, str) and loc.strip() and loc.lower() != "remote":
            locations.append(loc)

    # de-duplicate while preserving order
    def uniq(items: List[str]) -> List[str]:
        seen = set()
        out = []
        for item in items:
            key = item.lower()
            if key not in seen:
                seen.add(key)
                out.append(item)
        return out

    filters: Dict[str, Any] = {}
    if keywords:
        filters["keywords"] = uniq(keywords)
    if locations:
        filters["locations"] = uniq(locations)

    remote_pref = profile.get("remote_preference")
    if remote_pref == "only":
        filters["remote_only"] = True
    elif remote_pref == "prefer":
        filters["remote_preferred"] = True

    return filters


def merge_provider_filters(
    static_filters: Dict[str, Any] | None,
    dynamic_filters: Dict[str, Any] | None,
) -> Dict[str, Any]:
    static_filters = deepcopy(static_filters or {})
    dynamic_filters = dynamic_filters or {}
    merged: Dict[str, Any] = {}

    # list fields => union preserving static first
    for field in ("keywords", "locations"):
        values: List[str] = []
        for src in (static_filters.get(field) or []), (dynamic_filters.get(field) or []):
            for item in src:
                if isinstance(item, str) and item.strip():
                    if item.lower() not in {v.lower() for v in values}:
                        values.append(item)
        if values:
            merged[field] = values

    # boolean fields => static True wins, otherwise dynamic
    for field in ("remote_only", "remote_preferred"):
        if static_filters.get(field) is True:
            merged[field] = True
        elif dynamic_filters.get(field) is True:
            merged[field] = True

    # preserve any extra static fields if present
    for key, value in static_filters.items():
        if key not in merged and key not in ("keywords", "locations", "remote_only", "remote_preferred"):
            merged[key] = value

    return merged


def apply_dynamic_filters_to_sources(
    sources: List[Dict[str, Any]],
    profile: Dict[str, object],
) -> List[Dict[str, Any]]:
    dynamic = build_provider_filters_from_profile(profile)
    out: List[Dict[str, Any]] = []
    for source in sources:
        # Pass separator/comment objects through unchanged so fetch_all can skip them
        if source and all(k.startswith("_") for k in source.keys()):
            out.append(source)
            continue
        item = deepcopy(source)
        item["filters"] = merge_provider_filters(item.get("filters"), dynamic)
        out.append(item)
    return out
