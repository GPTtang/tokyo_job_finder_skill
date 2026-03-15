# Installation and mounting

## Local Python install
From the package root:

```bash
pip install -e .
```

## OpenClaw / Claude Code style usage
Mount this directory as a Skill package and point the runtime to `SKILL.md`.

Minimum files required:
- `SKILL.md`
- `job_finder/`
- `config/sources.example.json`

Recommended:
- `examples/`
- `docs/`

## Runtime expectations
- Python 3.10+
- outbound network access for configured public job sources
- optional local config file at `config/sources.json`

## Suggested deployment model
Use this Skill as a one-shot helper, not as a daemon or scheduled service.
