from __future__ import annotations

from .autofilters import apply_dynamic_filters_to_sources
from .config import load_config, validate_config
from .fetchers import fetch_all
from .formatter import build_report_payload, format_job_report
from .matcher import rank_jobs
from .parsers import parse_user_query


def run_job_finder(query: str, top_n: int = 5, config_path: str | None = None) -> dict:
    profile = parse_user_query(query)
    config = load_config(config_path)
    errors, warnings = validate_config(config)

    if errors:
        return {
            "ok": False,
            "error_type": "config_error",
            "errors": errors,
            "warnings": warnings,
            "profile": profile,
            "issues": [],
            "jobs": [],
        }

    dynamic_sources = apply_dynamic_filters_to_sources(
        config.get("sources", []),
        profile,
    )

    fetched = fetch_all(
        dynamic_sources,
        fetch_options=config.get("fetch_options", {}),
    )
    issues = fetched.get("issues", [])
    if warnings:
        issues = [
            {
                "provider": "config",
                "message": warning,
                "source_ref": config_path or "",
                "severity": "warning",
                "retryable": False,
                "details": {},
            }
            for warning in warnings
        ] + issues

    ranked = rank_jobs(profile, fetched.get("jobs", []), top_n=top_n)
    payload = build_report_payload(profile, ranked, issues=issues)
    payload["ok"] = True
    payload["profile"] = profile
    payload["effective_sources"] = dynamic_sources
    return payload


def job_finder(query: str, top_n: int = 5, config_path: str | None = None) -> str:
    payload = run_job_finder(query, top_n=top_n, config_path=config_path)
    if not payload.get("ok", False):
        message = "# 配置错误\n\n"
        message += "以下配置问题需要先修复：\n"
        for err in payload.get("errors", []):
            message += f"- {err}\n"
        if payload.get("warnings"):
            message += "\n附加提示：\n"
            for warning in payload.get("warnings", []):
                message += f"- {warning}\n"
        return message
    return format_job_report(
        payload.get("profile", {}),
        payload.get("jobs", []),
        issues=payload.get("issues", []),
    )
