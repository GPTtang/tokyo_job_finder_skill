# CLI usage

This version adds a local command-line entrypoint.

## Run directly as module
```bash
python -m job_finder.cli "I live in Japan and want Tokyo AI Engineer roles" --config config/sources.example.json --top-n 5
```

## Read query from file
```bash
python -m job_finder.cli --query-file examples/japan_ai_engineer.txt --config config/sources.example.json --top-n 5
```

## Smoke test
```bash
python smoke_test.py
```

## Exit codes
- `0`: success
- `1`: runtime failure
- `2`: argument or input error
- `130`: interrupted by user
