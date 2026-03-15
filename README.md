# job_finder Skill

`job_finder` is a single-run job-matching Skill for OpenClaw / Claude Code style workflows.

It takes a natural-language job search request, fetches jobs from configured public sources, ranks them against the user's profile, and returns a compact report.

## What this package is
- one Skill
- no database
- no persistent storage
- no SaaS backend
- no background workers

## Typical use case
- find AI / LLM / backend jobs in Japan
- compare jobs against a resume or self-description
- produce an application priority list

## Package layout
- `SKILL.md` — Skill contract
- `job_finder/` — implementation
- `config/sources.example.json` — example job sources
- `examples/` — runnable examples
- `docs/` — design and integration notes

## Quick start
```bash
python examples/demo_run.py
```

Or in Python:

```python
from job_finder.skill import job_finder

query = """
I live in Japan and want Tokyo or remote AI Engineer / LLM Engineer roles.
I have Python, FastAPI, RAG, vector search, and AI agent experience.
My Japanese is intermediate.
Find the best matching jobs for me.
"""

print(job_finder(query, top_n=5, config_path="config/sources.json"))
```

## Config
Copy:

```bash
cp config/sources.example.json config/sources.json
```

Then replace the example company / board values with the public sources you want to search.

## Notes
This package is intentionally small and ephemeral. It favors clear matching output over system complexity.


## Fetch tuning
`config/sources.example.json` supports runtime fetch options:

- `timeout_seconds`
- `max_retries`
- `retry_backoff_seconds`
- `max_follow_links`

This lets you tune source fetching without editing Python code.


## CLI
Run as a module:

```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5
```

After editable install:

```bash
job-finder --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5
```


## JSON output
For programmatic integration:

```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5 --output json --pretty
```

This is useful when wiring the Skill into a higher-level OpenClaw / Claude Code flow.


## Provider-level filters
Each source can now define pre-filters:

- `keywords`
- `locations`
- `remote_only`
- `remote_preferred`

Example:

```json
{
  "provider": "greenhouse",
  "token": "openai",
  "filters": {
    "keywords": ["AI", "LLM"],
    "locations": ["Tokyo"],
    "remote_preferred": true
  }
}
```


## Automatic provider filters
The Skill now derives provider filters from the user's query.

That means:
- role names become provider keywords
- detected skills become provider keywords
- detected locations become provider location filters
- remote preference becomes `remote_only` or `remote_preferred`

So you can keep `config/sources.example.json` mostly stable and let the Skill adapt per request.
