from pathlib import Path
from job_finder.cli import main

BASE = Path(__file__).resolve().parents[1]

query_file = BASE / "examples" / "japan_ai_engineer.txt"
config_file = BASE / "config" / "sources.example.json"

raise SystemExit(main([
    "--query-file", str(query_file),
    "--config", str(config_file),
    "--top-n", "3",
    "--output", "json",
    "--pretty",
]))
