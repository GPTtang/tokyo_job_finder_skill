from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

SUPPORTED_PROVIDERS = {
    "greenhouse": ["token"],
    "lever": ["company"],
    "ashby": ["board"],
    # Static HTML fetch + JSON-LD extraction (fast, no browser required)
    "company_site": ["url"],
    # Headless Playwright fetch — use for SPA/React/Vue/Next.js/Nuxt career pages
    # Requires: pip install playwright && playwright install chromium
    "browser_site": ["url"],
    # Built-in aggregators (static fetch + automatic browser fallback)
    "japan_dev": [],
    "gaijinpot": [],
    "tokyodev": [],
}

SUPPORTED_FILTER_FIELDS = {
    "keywords",
    "locations",
    "remote_only",
    "remote_preferred",
}

DEFAULT_FETCH_OPTIONS: Dict[str, Any] = {
    # requests-based fetch
    "timeout_seconds": 15,
    "max_retries": 1,
    "retry_backoff_seconds": 0.5,
    "max_follow_links": 3,
    # Playwright / browser_site options
    "browser_timeout_seconds": 30,   # page load timeout for headless browser
    "browser_wait_until": "networkidle",  # "load" | "domcontentloaded" | "networkidle"
}


_DEFAULT_CONFIG_PATH = Path("config/sources.json")


def load_config(config_path: str | None) -> Dict[str, Any]:
    if not config_path:
        if _DEFAULT_CONFIG_PATH.exists():
            config_path = str(_DEFAULT_CONFIG_PATH)
        else:
            return {"sources": [], "fetch_options": dict(DEFAULT_FETCH_OPTIONS)}

    path = Path(config_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    if "fetch_options" not in data:
        data["fetch_options"] = dict(DEFAULT_FETCH_OPTIONS)
    else:
        merged = dict(DEFAULT_FETCH_OPTIONS)
        merged.update(data.get("fetch_options") or {})
        data["fetch_options"] = merged
    if "sources" not in data:
        data["sources"] = []
    return data


def _validate_filters(filters: Any, source_idx: int, errors: List[str], warnings: List[str]) -> None:
    if filters is None:
        return
    if not isinstance(filters, dict):
        errors.append(f"`sources[{source_idx}].filters` 必须是对象。")
        return

    for key in filters.keys():
        if key not in SUPPORTED_FILTER_FIELDS:
            warnings.append(f"`sources[{source_idx}].filters.{key}` 不是当前支持的过滤字段。")

    for list_field in ("keywords", "locations"):
        if list_field in filters:
            value = filters[list_field]
            if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
                errors.append(f"`sources[{source_idx}].filters.{list_field}` 必须是非空字符串数组。")

    for bool_field in ("remote_only", "remote_preferred"):
        if bool_field in filters and not isinstance(filters[bool_field], bool):
            errors.append(f"`sources[{source_idx}].filters.{bool_field}` 必须是布尔值。")


def validate_config(config: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    sources = config.get("sources")
    if not isinstance(sources, list):
        errors.append("`sources` 必须是数组。")
        return errors, warnings

    fetch_options = config.get("fetch_options") or {}
    if not fetch_options:
        fetch_options = dict(DEFAULT_FETCH_OPTIONS)
    if not isinstance(fetch_options, dict):
        errors.append("`fetch_options` 必须是对象。")
    else:
        timeout = fetch_options.get("timeout_seconds")
        retries = fetch_options.get("max_retries")
        backoff = fetch_options.get("retry_backoff_seconds")
        max_follow = fetch_options.get("max_follow_links")
        browser_timeout = fetch_options.get("browser_timeout_seconds")
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            errors.append("`fetch_options.timeout_seconds` 必须是大于 0 的数字。")
        if not isinstance(retries, int) or retries < 0:
            errors.append("`fetch_options.max_retries` 必须是大于等于 0 的整数。")
        if not isinstance(backoff, (int, float)) or backoff < 0:
            errors.append("`fetch_options.retry_backoff_seconds` 必须是大于等于 0 的数字。")
        if not isinstance(max_follow, int) or max_follow < 0:
            errors.append("`fetch_options.max_follow_links` 必须是大于等于 0 的整数。")
        if browser_timeout is not None and (not isinstance(browser_timeout, (int, float)) or browser_timeout <= 0):
            errors.append("`fetch_options.browser_timeout_seconds` 必须是大于 0 的数字。")

    for i, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"`sources[{i}]` 必须是对象。")
            continue

        provider = source.get("provider")
        if provider not in SUPPORTED_PROVIDERS:
            errors.append(f"`sources[{i}].provider` 不支持：{provider!r}")
            continue

        required_fields = SUPPORTED_PROVIDERS[provider]
        for field in required_fields:
            value = source.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"`sources[{i}].{field}` 对于 provider={provider} 是必填字符串。")

        _validate_filters(source.get("filters"), i, errors, warnings)

        unknown_fields = sorted(set(source.keys()) - set(required_fields) - {"provider", "filters"})
        if unknown_fields:
            warnings.append(
                f"`sources[{i}]` 存在未使用字段：{', '.join(unknown_fields)}"
            )

    if not sources:
        warnings.append("当前配置没有任何职位源，Skill 只会返回空结果。")

    return errors, warnings
