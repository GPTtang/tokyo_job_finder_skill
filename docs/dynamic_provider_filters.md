# Automatic provider filters from user query

This version adds dynamic provider filters derived from the user's natural-language query.

## What changed
Previously, provider filters only came from static config in `sources.example.json`.

Now the Skill also derives filters from the parsed user profile:
- target roles -> `keywords`
- skills -> `keywords`
- location preferences -> `locations`
- remote preference -> `remote_only` or `remote_preferred`

These dynamic filters are merged into each configured source before fetching.

## Merge behavior
Static source filters and dynamic query filters are merged like this:

- `keywords`: union
- `locations`: union
- `remote_only`: true if either side requires it
- `remote_preferred`: true if either side prefers it and `remote_only` is not set

## Example
User query:
- “Tokyo or remote AI / LLM roles”
- “Python, RAG, FastAPI”

Generated dynamic filters:
```json
{
  "keywords": ["AI Engineer", "LLM Engineer", "Python", "RAG", "FastAPI"],
  "locations": ["Tokyo", "Japan"],
  "remote_preferred": true
}
```

## Why this helps
You no longer need to hardcode every query-specific filter in `sources.json`.
The config can stay relatively stable while the Skill adapts per run.
