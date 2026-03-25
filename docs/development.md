# Development Reference

## Architecture

The Skill is intentionally ephemeral: fetch → match → report, with no database or background sync.

```
job_finder/
├── skill.py        # public entry point: job_finder(query, top_n, config_path)
├── cli.py          # CLI wrapper around skill.py
├── config.py       # load/validate sources.json and priority_companies.json
├── fetchers.py     # per-provider HTTP / browser fetchers, returns {jobs, issues}
├── parsers.py      # parse natural-language query → structured profile
├── autofilters.py  # merge query-derived filters into static source configs
├── matcher.py      # score and rank jobs against profile
└── formatter.py    # render final report (text or JSON)
```

## Installation

```bash
pip install -e .

# Optional: headless browser support for JS-rendered career pages
pip install -e ".[browser]"
playwright install chromium
```

## CLI usage

```bash
# Inline query
python -m job_finder.cli "I live in Japan and want Tokyo AI Engineer roles" \
  --config config/sources.example.json --top-n 5

# Query from file
python -m job_finder.cli --query-file examples/queries/ai_engineer.txt \
  --config config/sources.example.json --top-n 5

# JSON output
python -m job_finder.cli --query-file examples/queries/ai_engineer.txt \
  --config config/sources.example.json --top-n 5 --output json --pretty
```

Exit codes: `0` success · `1` runtime failure · `2` bad arguments · `130` interrupted

## JSON payload shape

```
ok, profile, summary, jobs, issues, suggestions, effective_sources
```

On config error: `ok: false, error_type: "config_error", errors, warnings`

## Provider matrix

| Provider       | Fetch method       | Structured data | Notes |
|----------------|--------------------|-----------------|-------|
| `greenhouse`   | JSON API           | Strong          | Western ATS; most JP companies don't use it |
| `lever`        | JSON API           | Strong          | Good for startup postings |
| `ashby`        | JSON API           | Strong          | Use when company is on Ashby |
| `company_site` | Static HTML fetch  | Weak–medium     | JSON-LD → link-follow → heuristic fallback |
| `browser_site` | Playwright (headless) | Medium       | For SPA/React/Vue/Next.js/Nuxt career pages |
| `japan_dev`    | browser_site built-in | Medium      | Aggregator: ~60 jobs |
| `gaijinpot`    | browser_site built-in | Low         | Aggregator: requires login for full results |
| `tokyodev`     | browser_site built-in | Strong      | Aggregator: ~177 jobs |

## Source config: fetch_options

```json
{
  "fetch_options": {
    "timeout_seconds": 15,
    "max_retries": 1,
    "retry_backoff_seconds": 0.5,
    "max_follow_links": 3,
    "max_concurrent_fetches": 4,
    "browser_timeout_seconds": 30,
    "browser_wait_until": "domcontentloaded"
  }
}
```

## Provider-level filters

```json
{
  "provider": "greenhouse",
  "token": "openai",
  "filters": {
    "keywords": ["AI", "Engineer"],
    "locations": ["Tokyo", "Japan"],
    "remote_preferred": true
  }
}
```

Filter semantics:
- `keywords`: job kept if title/description/skills contains ≥1 keyword
- `locations`: job kept if location contains ≥1 value
- `remote_only`: keep only remote jobs
- `remote_preferred`: sort remote jobs first

## Dynamic filters from query

The user's natural-language query is parsed and merged into each source's filters automatically:

- extracted roles → `keywords`
- extracted skills → `keywords`
- extracted locations → `locations`
- remote intent → `remote_only` / `remote_preferred`

Static config filters and dynamic query filters are unioned (keywords/locations) or OR-ed (booleans).

## Scoring formula

```
score = 0.5 × skill_match
      + 0.3 × title_match
      + 0.2 × location_match
      + 0.25  (if named priority company)   ← config/priority_companies.json
      + 0.20  (if Chinese IT 乙方 signal)
      + 0.15  (if Chinese speaker + job signals 中国語優遇)
      + 0.10  (if Chinese speaker + Bridge SE role)
      − 0.20  (if JLPT requirement exceeds candidate level)
      clamped to [0.0, 1.0]
```

## Error handling

Each fetch issue is returned as a structured object rather than crashing:

```json
{
  "provider": "greenhouse",
  "message": "HTTP 404",
  "source_ref": "https://...",
  "severity": "warning",
  "retryable": false,
  "details": {}
}
```

Partial failures degrade gracefully; the Skill continues with successful sources.

## Running tests

```bash
python3 -m pytest tests/ -q
```

## Deployment model

Use as a one-shot Skill helper, not as a daemon or scheduled service.
Minimum files for deployment: `SKILL.md`, `job_finder/`, `config/sources.example.json`
