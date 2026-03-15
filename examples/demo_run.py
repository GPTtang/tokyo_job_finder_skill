from pathlib import Path
from job_finder.skill import job_finder

BASE = Path(__file__).resolve().parents[1]
query = (BASE / "examples" / "japan_ai_engineer.txt").read_text(encoding="utf-8")
config_path = BASE / "config" / "sources.example.json"

print(job_finder(query, top_n=5, config_path=str(config_path)))
