# Config validation and fetch options

This version adds two practical hardening features:

## 1. Source config validation
Before any fetch starts, the Skill validates:
- `sources` exists and is a list
- every provider is supported
- required fields are present
- fetch option types are valid

If validation fails, the Skill returns a clear configuration error report instead of failing deeper inside a provider.

## 2. Timeout and retry controls
`config/sources.example.json` now supports:

- `timeout_seconds`
- `max_retries`
- `retry_backoff_seconds`
- `max_follow_links`

These options are passed into the fetch layer so the Skill can be tuned without changing code.

## Example
```json
{
  "fetch_options": {
    "timeout_seconds": 20,
    "max_retries": 2,
    "retry_backoff_seconds": 1.0,
    "max_follow_links": 5
  },
  "sources": [
    {"provider": "greenhouse", "token": "openai"}
  ]
}
```
