# Structured fetch error handling

This version adds a simple unified error structure for source fetching.

## Why
Different public job sources fail in different ways:
- HTTP 404 when a board slug changes
- HTTP 429 / 403 when a source blocks access
- malformed or non-JSON responses
- careers pages with no structured `JobPosting` data

Without a common structure, the Skill output becomes unstable.

## New model
The fetch layer now returns:

- `jobs`: normalized jobs
- `issues`: a list of structured issue objects

Each issue contains:
- `provider`
- `message`
- `source_ref`
- `severity`
- `retryable`
- `details`

## Behavior
- Partial failures no longer break the whole run.
- The formatter includes a brief fetch-status section.
- The Skill still returns the best available matches from successful sources.

## Example issue
```json
{
  "provider": "greenhouse",
  "message": "HTTP 404",
  "source_ref": "https://boards-api.greenhouse.io/...",
  "severity": "warning",
  "retryable": false,
  "details": {}
}
```
