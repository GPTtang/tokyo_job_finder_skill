# CLI JSON output mode

This version adds a machine-friendly JSON output mode.

## Text mode
```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5
```

## JSON mode
```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5 --output json
```

## Pretty JSON
```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5 --output json --pretty
```

## JSON payload shape
- `ok`
- `profile`
- `summary`
- `issues`
- `jobs`
- `suggestions`

If configuration validation fails, JSON mode returns:
- `ok: false`
- `error_type: "config_error"`
- `errors`
- `warnings`


## Extra JSON field
JSON mode now also returns:

- `effective_sources`

This shows the configured sources after dynamic provider filters from the user query have been merged in.
