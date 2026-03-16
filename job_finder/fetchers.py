from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from html import unescape
from typing import Any, Dict, Iterable, List, Optional, Tuple
from urllib.parse import urljoin

import requests


@dataclass
class FetchIssue:
    provider: str
    message: str
    source_ref: str = ""
    severity: str = "warning"
    retryable: bool = False
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FetchResult:
    provider: str
    jobs: List[Dict[str, Any]] = field(default_factory=list)
    issues: List[FetchIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.jobs) > 0 and not any(i.severity == "error" for i in self.issues)


def make_job(
    *,
    title: str,
    company: str,
    location: str = "",
    url: str = "",
    description: str = "",
    source: str = "",
    skills: Optional[List[str]] = None,
    remote: Optional[bool] = None,
    posted_date: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "title": title or "",
        "company": company or "",
        "location": location or "",
        "url": url or "",
        "description": description or "",
        "source": source or "",
        "skills": skills or [],
        "remote": remote,
        "posted_date": posted_date,
    }


def _http_get(
    url: str,
    *,
    provider: str,
    timeout_seconds: float,
    max_retries: int,
    retry_backoff_seconds: float,
) -> Tuple[Optional[requests.Response], List[FetchIssue]]:
    issues: List[FetchIssue] = []
    attempts = max_retries + 1

    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(
                url,
                timeout=timeout_seconds,
                headers={"User-Agent": "job-finder-skill/1.2"},
            )
        except requests.RequestException as exc:
            retryable = attempt < attempts
            issues.append(FetchIssue(
                provider=provider,
                source_ref=url,
                message=f"Network error on attempt {attempt}/{attempts}: {exc}",
                severity="error" if not retryable else "warning",
                retryable=retryable,
                details={"attempt": attempt, "attempts": attempts},
            ))
            if retryable:
                time.sleep(retry_backoff_seconds)
                continue
            return None, issues

        if response.status_code >= 500 and attempt < attempts:
            issues.append(FetchIssue(
                provider=provider,
                source_ref=url,
                message=f"HTTP {response.status_code} on attempt {attempt}/{attempts}",
                severity="warning",
                retryable=True,
                details={"attempt": attempt, "attempts": attempts},
            ))
            time.sleep(retry_backoff_seconds)
            continue

        return response, issues

    return None, issues


def _safe_get_json(
    url: str,
    *,
    provider: str,
    timeout_seconds: float,
    max_retries: int,
    retry_backoff_seconds: float,
) -> tuple[Optional[Any], List[FetchIssue]]:
    response, issues = _http_get(
        url,
        provider=provider,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    if response is None:
        return None, issues

    if response.status_code >= 400:
        issues.append(FetchIssue(
            provider=provider,
            source_ref=url,
            message=f"HTTP {response.status_code}",
            severity="error" if response.status_code >= 500 else "warning",
            retryable=response.status_code >= 500,
        ))
        return None, issues

    try:
        return response.json(), issues
    except ValueError:
        issues.append(FetchIssue(
            provider=provider,
            source_ref=url,
            message="Response was not valid JSON",
            severity="error",
            retryable=False,
        ))
        return None, issues


def _safe_get_text(
    url: str,
    *,
    provider: str,
    timeout_seconds: float,
    max_retries: int,
    retry_backoff_seconds: float,
) -> tuple[Optional[str], List[FetchIssue]]:
    response, issues = _http_get(
        url,
        provider=provider,
        timeout_seconds=timeout_seconds,
        max_retries=max_retries,
        retry_backoff_seconds=retry_backoff_seconds,
    )
    if response is None:
        return None, issues

    if response.status_code >= 400:
        issues.append(FetchIssue(
            provider=provider,
            source_ref=url,
            message=f"HTTP {response.status_code}",
            severity="error" if response.status_code >= 500 else "warning",
            retryable=response.status_code >= 500,
        ))
        return None, issues

    return response.text, issues


def _html_to_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = unescape(value)
    value = re.sub(r"\s+", " ", value).strip()
    return value


def _extract_basic_skills(text: str) -> List[str]:
    vocab = [
        "Python", "FastAPI", "RAG", "LLM", "LangChain", "LangGraph",
        "OpenSearch", "Elasticsearch", "Qdrant", "FAISS",
        "AWS", "GCP", "Azure", "Docker", "Kubernetes",
        "PyTorch", "TensorFlow", "Go", "TypeScript", "React",
        "Agent", "Vector Search", "Machine Learning",
    ]
    text_l = (text or "").lower()
    return [skill for skill in vocab if skill.lower() in text_l]


def _job_text(job: Dict[str, Any]) -> str:
    text = " ".join([
        str(job.get("title", "")),
        str(job.get("company", "")),
        str(job.get("location", "")),
        str(job.get("description", "")),
        " ".join(job.get("skills", []) or []),
    ])
    return text.lower()


def _apply_source_filters(
    jobs: List[Dict[str, Any]],
    filters: Dict[str, Any] | None,
    provider: str,
) -> tuple[List[Dict[str, Any]], List[FetchIssue]]:
    if not filters:
        return jobs, []

    issues: List[FetchIssue] = []
    filtered = jobs

    keywords = filters.get("keywords") or []
    if keywords:
        keywords_l = [k.lower() for k in keywords]
        filtered = [
            job for job in filtered
            if any(k in _job_text(job) for k in keywords_l)
        ]

    locations = filters.get("locations") or []
    if locations:
        locations_l = [loc.lower() for loc in locations]
        filtered = [
            job for job in filtered
            if any(loc in str(job.get("location", "")).lower() for loc in locations_l)
        ]

    if filters.get("remote_only"):
        filtered = [job for job in filtered if job.get("remote") is True]
    elif filters.get("remote_preferred"):
        remote_jobs = [job for job in filtered if job.get("remote") is True]
        non_remote_jobs = [job for job in filtered if job.get("remote") is not True]
        filtered = remote_jobs + non_remote_jobs

    if not filtered and jobs:
        issues.append(FetchIssue(
            provider=provider,
            message="Provider-level filters removed all fetched jobs",
            severity="warning",
            retryable=False,
            details={"filters": filters, "original_count": len(jobs)},
        ))

    return filtered, issues


def fetch_greenhouse(token: str, fetch_options: Dict[str, Any] | None = None) -> FetchResult:
    provider = "greenhouse"
    fetch_options = fetch_options or {}
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    data, issues = _safe_get_json(
        url,
        provider=provider,
        timeout_seconds=fetch_options.get("timeout_seconds", 15),
        max_retries=fetch_options.get("max_retries", 1),
        retry_backoff_seconds=fetch_options.get("retry_backoff_seconds", 0.5),
    )
    result = FetchResult(provider=provider, issues=issues)

    if not data:
        return result

    jobs = []
    for item in data.get("jobs", []):
        content = item.get("content", "") or ""
        location_name = (item.get("location") or {}).get("name", "")
        jobs.append(make_job(
            title=item.get("title", ""),
            company=token,
            location=location_name,
            url=item.get("absolute_url", ""),
            description=_html_to_text(content),
            source=provider,
            skills=_extract_basic_skills(content),
            remote="remote" in location_name.lower(),
            posted_date=item.get("updated_at") or item.get("created_at"),
        ))

    if not jobs:
        result.issues.append(FetchIssue(
            provider=provider,
            source_ref=url,
            message="No jobs returned from source",
            severity="warning",
            retryable=False,
        ))
    result.jobs = jobs
    return result


def fetch_lever(company: str, fetch_options: Dict[str, Any] | None = None) -> FetchResult:
    provider = "lever"
    fetch_options = fetch_options or {}
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    data, issues = _safe_get_json(
        url,
        provider=provider,
        timeout_seconds=fetch_options.get("timeout_seconds", 15),
        max_retries=fetch_options.get("max_retries", 1),
        retry_backoff_seconds=fetch_options.get("retry_backoff_seconds", 0.5),
    )
    result = FetchResult(provider=provider, issues=issues)

    if not data:
        return result

    jobs = []
    for item in data:
        categories = item.get("categories", {}) or {}
        location = categories.get("location", "") or ""
        raw_desc = " ".join([
            item.get("descriptionPlain", "") or "",
            item.get("lists", [{}])[0].get("text", "") if item.get("lists") else "",
        ])
        jobs.append(make_job(
            title=item.get("text", ""),
            company=company,
            location=location,
            url=item.get("hostedUrl", ""),
            description=_html_to_text(raw_desc),
            source=provider,
            skills=_extract_basic_skills(raw_desc),
            remote="remote" in location.lower(),
            posted_date=item.get("createdAt"),
        ))

    if not jobs:
        result.issues.append(FetchIssue(
            provider=provider,
            source_ref=url,
            message="No jobs returned from source",
            severity="warning",
            retryable=False,
        ))
    result.jobs = jobs
    return result


def fetch_ashby(board: str, fetch_options: Dict[str, Any] | None = None) -> FetchResult:
    provider = "ashby"
    fetch_options = fetch_options or {}
    url = f"https://api.ashbyhq.com/posting-api/job-board/{board}?includeCompensation=true"
    data, issues = _safe_get_json(
        url,
        provider=provider,
        timeout_seconds=fetch_options.get("timeout_seconds", 15),
        max_retries=fetch_options.get("max_retries", 1),
        retry_backoff_seconds=fetch_options.get("retry_backoff_seconds", 0.5),
    )
    result = FetchResult(provider=provider, issues=issues)

    if not data:
        return result

    jobs = []
    for item in data.get("jobs", []):
        desc = item.get("descriptionPlain", "") or item.get("descriptionHtml", "") or ""
        location = item.get("location", "") or ""
        jobs.append(make_job(
            title=item.get("title", ""),
            company=board,
            location=location,
            url=item.get("jobUrl", ""),
            description=_html_to_text(desc),
            source=provider,
            skills=_extract_basic_skills(desc),
            remote="remote" in location.lower(),
            posted_date=item.get("publishedDate"),
        ))

    if not jobs:
        result.issues.append(FetchIssue(
            provider=provider,
            source_ref=url,
            message="No jobs returned from source",
            severity="warning",
            retryable=False,
        ))
    result.jobs = jobs
    return result


def _extract_json_ld_jobpostings(html: str, base_url: str) -> List[Dict[str, Any]]:
    jobs = []
    scripts = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html,
        flags=re.I | re.S,
    )
    for raw in scripts:
        try:
            data = json.loads(raw.strip())
        except Exception:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                jobs.append(make_job(
                    title=item.get("title", ""),
                    company=((item.get("hiringOrganization") or {}).get("name", "")),
                    location=(((item.get("jobLocation") or {}).get("address") or {}).get("addressLocality", "")),
                    url=base_url,
                    description=_html_to_text(item.get("description", "")),
                    source="company_site",
                    skills=_extract_basic_skills(item.get("description", "")),
                    remote=item.get("jobLocationType") == "TELECOMMUTE",
                    posted_date=item.get("datePosted"),
                ))
    return jobs


def fetch_company_site(url: str, fetch_options: Dict[str, Any] | None = None) -> FetchResult:
    provider = "company_site"
    fetch_options = fetch_options or {}
    html, issues = _safe_get_text(
        url,
        provider=provider,
        timeout_seconds=fetch_options.get("timeout_seconds", 15),
        max_retries=fetch_options.get("max_retries", 1),
        retry_backoff_seconds=fetch_options.get("retry_backoff_seconds", 0.5),
    )
    result = FetchResult(provider=provider, issues=issues)

    if not html:
        return result

    jobs = _extract_json_ld_jobpostings(html, url)
    if jobs:
        result.jobs = jobs
        return result

    hrefs = re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.I)
    candidate_links = []
    keywords = ("job", "jobs", "career", "careers", "recruit", "position", "opening")
    for href in hrefs:
        href_l = href.lower()
        if any(k in href_l for k in keywords):
            full = urljoin(url, href)
            if full not in candidate_links:
                candidate_links.append(full)

    followed = 0
    max_follow_links = fetch_options.get("max_follow_links", 3)
    for link in candidate_links[:max_follow_links]:
        followed += 1
        child_html, child_issues = _safe_get_text(
            link,
            provider=provider,
            timeout_seconds=fetch_options.get("timeout_seconds", 15),
            max_retries=fetch_options.get("max_retries", 1),
            retry_backoff_seconds=fetch_options.get("retry_backoff_seconds", 0.5),
        )
        result.issues.extend(child_issues)
        if not child_html:
            continue
        child_jobs = _extract_json_ld_jobpostings(child_html, link)
        jobs.extend(child_jobs)

    if followed == 0:
        result.issues.append(FetchIssue(
            provider=provider,
            source_ref=url,
            message="No likely careers links discovered",
            severity="warning",
            retryable=False,
        ))
    elif not jobs:
        result.issues.append(FetchIssue(
            provider=provider,
            source_ref=url,
            message="Careers page discovered, but no JSON-LD JobPosting extracted",
            severity="warning",
            retryable=False,
            details={"followed_links": followed},
        ))

    result.jobs = jobs
    return result


def _scan_for_jobs(data: Any, source_url: str) -> List[Dict[str, Any]]:
    """Recursively scan a nested data structure for job-like records."""
    jobs: List[Dict[str, Any]] = []
    if isinstance(data, dict):
        title = data.get("title") or data.get("name") or data.get("job_title")
        company = data.get("company") or data.get("company_name") or data.get("employer")
        if title and company and isinstance(title, str) and isinstance(company, str):
            desc = str(data.get("description") or data.get("body") or "")
            jobs.append(make_job(
                title=title,
                company=company,
                location=str(data.get("location") or data.get("city") or ""),
                url=str(data.get("url") or data.get("job_url") or data.get("apply_url") or source_url),
                description=_html_to_text(desc),
                source="japan_dev",
                skills=_extract_basic_skills(desc),
            ))
        else:
            for v in data.values():
                jobs.extend(_scan_for_jobs(v, source_url))
    elif isinstance(data, list):
        for item in data:
            jobs.extend(_scan_for_jobs(item, source_url))
    return jobs


def fetch_japan_dev(fetch_options: Dict[str, Any] | None = None) -> FetchResult:
    """Fetch jobs from japan-dev.com.

    japan-dev.com is a Nuxt/Vue SPA backed by Algolia search.  This fetcher
    attempts to extract SSR-hydrated job data injected by the server (Nuxt 2
    ``window.__NUXT__`` or Nuxt 3 ``<script id="__NUXT_DATA__">`` patterns)
    and falls back to JSON-LD extraction.  Results may be empty when the page
    is fully client-side rendered; in that case a descriptive warning is
    emitted so callers can take alternative action (e.g. a headless browser).
    """
    provider = "japan_dev"
    fetch_options = fetch_options or {}
    url = "https://japan-dev.com/jobs"
    html, issues = _safe_get_text(
        url,
        provider=provider,
        timeout_seconds=fetch_options.get("timeout_seconds", 15),
        max_retries=fetch_options.get("max_retries", 1),
        retry_backoff_seconds=fetch_options.get("retry_backoff_seconds", 0.5),
    )
    result = FetchResult(provider=provider, issues=issues)
    if not html:
        return result

    jobs: List[Dict[str, Any]] = []

    # Nuxt 3: <script id="__NUXT_DATA__" type="application/json">…</script>
    for raw in re.findall(
        r'<script[^>]+id=["\']__NUXT_DATA__["\'][^>]*>(.*?)</script>',
        html,
        flags=re.I | re.S,
    ):
        try:
            jobs.extend(_scan_for_jobs(json.loads(raw.strip()), url))
        except Exception:
            pass

    # Nuxt 2: window.__NUXT__ = {…};
    if not jobs:
        for m in re.finditer(r'window\.__NUXT__\s*=\s*(\{.*?\})\s*(?:;|</script>)', html, re.S):
            try:
                jobs.extend(_scan_for_jobs(json.loads(m.group(1)), url))
            except Exception:
                pass

    # Generic JSON-LD fallback
    if not jobs:
        jobs.extend(_extract_json_ld_jobpostings(html, url))

    if not jobs:
        result.issues.append(FetchIssue(
            provider=provider,
            source_ref=url,
            message=(
                "japan-dev.com appears to be fully client-side rendered via Algolia; "
                "no job data extracted from static HTML. "
                "A headless browser is required for reliable extraction."
            ),
            severity="warning",
            retryable=False,
        ))

    result.jobs = jobs
    return result


def fetch_gaijinpot(fetch_options: Dict[str, Any] | None = None) -> FetchResult:
    """Fetch jobs from GaijinPot Jobs (jobs.gaijinpot.com).

    GaijinPot targets foreign workers in Japan and commonly lists positions
    with JLPT N2/N3 requirements — a good fit for Chinese speakers who don't
    yet hold N1.  The site is partially client-side rendered; results may be
    sparse without a headless browser.
    """
    provider = "gaijinpot"
    fetch_options = fetch_options or {}
    base_url = "https://jobs.gaijinpot.com"
    search_url = f"{base_url}/job/index/search"

    # Try the JSON search endpoint first
    data, issues = _safe_get_json(
        search_url,
        provider=provider,
        timeout_seconds=fetch_options.get("timeout_seconds", 15),
        max_retries=fetch_options.get("max_retries", 1),
        retry_backoff_seconds=fetch_options.get("retry_backoff_seconds", 0.5),
    )
    result = FetchResult(provider=provider, issues=issues)

    if data:
        jobs = _scan_for_jobs(data, search_url)
        if jobs:
            result.jobs = jobs
            return result

    # Fall back to HTML scraping of the listings page
    html, html_issues = _safe_get_text(
        base_url,
        provider=provider,
        timeout_seconds=fetch_options.get("timeout_seconds", 15),
        max_retries=fetch_options.get("max_retries", 1),
        retry_backoff_seconds=fetch_options.get("retry_backoff_seconds", 0.5),
    )
    result.issues.extend(html_issues)

    jobs: List[Dict[str, Any]] = []
    if html:
        jobs.extend(_extract_json_ld_jobpostings(html, base_url))
        if not jobs:
            for raw in re.findall(
                r'<script[^>]+type=["\']application/json["\'][^>]*>(.*?)</script>',
                html,
                flags=re.I | re.S,
            ):
                try:
                    jobs.extend(_scan_for_jobs(json.loads(raw.strip()), base_url))
                except Exception:
                    pass

    if not jobs:
        result.issues.append(FetchIssue(
            provider=provider,
            source_ref=base_url,
            message=(
                "GaijinPot Jobs appears to be client-side rendered; "
                "no job data extracted from static HTML. "
                "A headless browser is required for reliable extraction."
            ),
            severity="warning",
            retryable=False,
        ))

    result.jobs = jobs
    return result


def fetch_tokyodev(fetch_options: Dict[str, Any] | None = None) -> FetchResult:
    """Fetch jobs from TokyoDev (tokyodev.com/jobs).

    TokyoDev lists developer positions in Japan that are open to non-Japanese
    speakers.  Many roles specify English as the working language and do not
    require Japanese above N2, making it a strong source for Chinese-speaking
    engineers.
    """
    provider = "tokyodev"
    fetch_options = fetch_options or {}
    base_url = "https://www.tokyodev.com"
    jobs_url = f"{base_url}/jobs"

    html, issues = _safe_get_text(
        jobs_url,
        provider=provider,
        timeout_seconds=fetch_options.get("timeout_seconds", 15),
        max_retries=fetch_options.get("max_retries", 1),
        retry_backoff_seconds=fetch_options.get("retry_backoff_seconds", 0.5),
    )
    result = FetchResult(provider=provider, issues=issues)

    if not html:
        return result

    jobs: List[Dict[str, Any]] = []

    # Next.js / React hydration blobs
    for raw in re.findall(
        r'<script[^>]+id=["\']__NEXT_DATA__["\'][^>]*>(.*?)</script>',
        html,
        flags=re.I | re.S,
    ):
        try:
            jobs.extend(_scan_for_jobs(json.loads(raw.strip()), jobs_url))
        except Exception:
            pass

    # Generic JSON-LD fallback
    if not jobs:
        jobs.extend(_extract_json_ld_jobpostings(html, jobs_url))

    # Generic application/json script tags
    if not jobs:
        for raw in re.findall(
            r'<script[^>]+type=["\']application/json["\'][^>]*>(.*?)</script>',
            html,
            flags=re.I | re.S,
        ):
            try:
                jobs.extend(_scan_for_jobs(json.loads(raw.strip()), jobs_url))
            except Exception:
                pass

    if not jobs:
        result.issues.append(FetchIssue(
            provider=provider,
            source_ref=jobs_url,
            message=(
                "TokyoDev appears to be client-side rendered; "
                "no job data extracted from static HTML. "
                "A headless browser is required for reliable extraction."
            ),
            severity="warning",
            retryable=False,
        ))

    result.jobs = jobs
    return result


def fetch_from_source(source: Dict[str, Any], fetch_options: Dict[str, Any] | None = None) -> FetchResult:
    provider = source.get("provider")
    filters = source.get("filters")

    if provider == "greenhouse":
        result = fetch_greenhouse(source["token"], fetch_options=fetch_options)
    elif provider == "lever":
        result = fetch_lever(source["company"], fetch_options=fetch_options)
    elif provider == "ashby":
        result = fetch_ashby(source["board"], fetch_options=fetch_options)
    elif provider == "company_site":
        result = fetch_company_site(source["url"], fetch_options=fetch_options)
    elif provider == "japan_dev":
        result = fetch_japan_dev(fetch_options=fetch_options)
    elif provider == "gaijinpot":
        result = fetch_gaijinpot(fetch_options=fetch_options)
    elif provider == "tokyodev":
        result = fetch_tokyodev(fetch_options=fetch_options)
    else:
        return FetchResult(
            provider=str(provider or "unknown"),
            issues=[
                FetchIssue(
                    provider=str(provider or "unknown"),
                    message="Unsupported provider in source config",
                    severity="error",
                    retryable=False,
                    details={"source": source},
                )
            ],
        )

    filtered_jobs, filter_issues = _apply_source_filters(result.jobs, filters, provider=str(provider))
    result.jobs = filtered_jobs
    result.issues.extend(filter_issues)
    return result


def fetch_all(sources: Iterable[Dict[str, Any]], fetch_options: Dict[str, Any] | None = None) -> Dict[str, Any]:
    all_jobs: List[Dict[str, Any]] = []
    all_issues: List[Dict[str, Any]] = []

    for source in sources:
        result = fetch_from_source(source, fetch_options=fetch_options)
        all_jobs.extend(result.jobs)
        all_issues.extend([
            {
                "provider": issue.provider,
                "message": issue.message,
                "source_ref": issue.source_ref,
                "severity": issue.severity,
                "retryable": issue.retryable,
                "details": issue.details,
            }
            for issue in result.issues
        ])

    return {
        "jobs": all_jobs,
        "issues": all_issues,
    }


def seed_jobs() -> List[Dict[str, Any]]:
    """Return a small deterministic dataset for smoke tests and examples."""
    return [
        make_job(
            title="AI Platform Engineer",
            company="Tokyo GenAI Lab",
            location="Tokyo, Japan",
            description="Build internal agents and retrieval pipelines for enterprise clients.",
            source="seed",
            skills=["Python", "RAG", "FastAPI", "Agent"],
            remote=False,
        ),
        make_job(
            title="Applied Scientist",
            company="Kyoto Intelligence",
            location="Kyoto, Japan",
            description="Research-oriented GenAI role using LangChain and vector DBs.",
            source="seed",
            skills=["Python", "LangChain", "Qdrant", "RAG"],
            remote=True,
        ),
        make_job(
            title="Full-Stack LLM Engineer",
            company="Osaka AI Works",
            location="Osaka, Japan",
            description="Ship LLM backed products using TypeScript/React frontends.",
            source="seed",
            skills=["Python", "TypeScript", "React", "Agent"],
            remote=True,
        ),
        make_job(
            title="Machine Learning Engineer",
            company="Sapporo Robotics",
            location="Remote (Japan)",
            description="Expand ML platforms with Kubernetes and AWS infrastructure.",
            source="seed",
            skills=["Python", "AWS", "Kubernetes", "FastAPI"],
            remote=True,
        ),
    ]
