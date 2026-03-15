# Provider-level filters

This version adds source-level pre-filters so each provider can narrow jobs before global ranking.

## Supported filters
Inside each source, you can now add:

- `keywords`: list of strings
- `locations`: list of strings
- `remote_only`: boolean
- `remote_preferred`: boolean

## Example
```json
{
  "provider": "greenhouse",
  "token": "openai",
  "filters": {
    "keywords": ["AI", "Engineer", "LLM"],
    "locations": ["Tokyo", "Japan"],
    "remote_preferred": true
  }
}
```

## Behavior
- `keywords`: keeps jobs whose title, company, location, description, or skills contain at least one keyword
- `locations`: keeps jobs whose location contains at least one configured location
- `remote_only`: keeps only jobs with `remote == true`
- `remote_preferred`: reorders provider results so remote jobs come first

## Notes
These filters run **inside each provider result** before global ranking.
That makes the Skill more efficient and reduces noise for mixed sources.
