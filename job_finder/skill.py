from __future__ import annotations

import json

from .autofilters import apply_dynamic_filters_to_sources
from .config import load_config, load_priority_companies, validate_config
from .fetchers import fetch_all
from .formatter import build_report_payload, format_job_report
from .matcher import rank_jobs
from .parsers import parse_user_query


def _config_error_response(profile: dict, errors: list[str], warnings: list[str] | None = None) -> dict:
    return {
        "ok": False,
        "error_type": "config_error",
        "errors": errors,
        "warnings": warnings or [],
        "profile": profile,
        "issues": [],
        "jobs": [],
    }


def run_job_finder(
    query: str,
    top_n: int = 5,
    config_path: str | None = None,
    priority_path: str | None = None,
) -> dict:
    profile = parse_user_query(query)
    try:
        config = load_config(config_path)
    except FileNotFoundError as exc:
        return _config_error_response(
            profile,
            [
                "未找到 sources 配置文件，请先运行 `cp config/sources.example.json config/sources.json` "
                "或在 --config 中提供路径。",
                str(exc),
            ],
        )
    except json.JSONDecodeError as exc:
        return _config_error_response(
            profile,
            [f"配置 JSON 解析失败：{exc}"],
        )
    except OSError as exc:
        return _config_error_response(
            profile,
            [f"读取配置文件失败：{exc}"],
        )
    errors, warnings = validate_config(config)

    if errors:
        return _config_error_response(profile, errors, warnings)

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

    priority_cfg = load_priority_companies(priority_path)
    ranked = rank_jobs(profile, fetched.get("jobs", []), top_n=top_n, priority_cfg=priority_cfg)
    payload = build_report_payload(profile, ranked, issues=issues)
    payload["ok"] = True
    payload["profile"] = profile
    payload["effective_sources"] = dynamic_sources
    return payload


def job_finder(
    query: str,
    top_n: int = 5,
    config_path: str | None = None,
    priority_path: str | None = None,
) -> str:
    payload = run_job_finder(query, top_n=top_n, config_path=config_path, priority_path=priority_path)
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
