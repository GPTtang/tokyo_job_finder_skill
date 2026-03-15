# Production-style packaging notes

This package is still intentionally lightweight, but it now looks closer to a production-ready Skill bundle.

## Added in this version
- stronger `SKILL.md`
- `config/sources.example.json`
- install / mount guide
- multiple example prompt scenarios
- clearer README

## Why no database
The project is deliberately scoped as an ephemeral Skill:
- fetch now
- match now
- report now

That keeps it aligned with the intended Skill use case and avoids accidental platform sprawl.

## Recommended next hardening steps
1. add source-specific timeout and retry controls
2. add structured fetch error reporting
3. add unit tests for parser / formatter
4. add optional HTML sanitization for job descriptions
5. add provider capability matrix in docs
