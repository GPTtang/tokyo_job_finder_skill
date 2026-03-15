from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .skill import job_finder, run_job_finder


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="job-finder",
        description="Single-run job finder Skill CLI",
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Natural-language job search query. If omitted, use --query-file.",
    )
    parser.add_argument(
        "--query-file",
        type=str,
        help="Path to a text file containing the natural-language query.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to sources config JSON.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of ranked jobs to return.",
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON output.",
    )
    return parser


def _read_query(args: argparse.Namespace) -> str:
    if args.query:
        return args.query.strip()
    if args.query_file:
        return Path(args.query_file).read_text(encoding="utf-8").strip()
    raise ValueError("必须提供 query 或 --query-file。")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        query = _read_query(args)
    except Exception as exc:
        print(f"参数错误：{exc}", file=sys.stderr)
        return 2

    try:
        if args.output == "json":
            payload = run_job_finder(query, top_n=args.top_n, config_path=args.config)
            if args.pretty:
                print(json.dumps(payload, ensure_ascii=False, indent=2))
            else:
                print(json.dumps(payload, ensure_ascii=False))
            return 0 if payload.get("ok", False) else 1

        output = job_finder(query, top_n=args.top_n, config_path=args.config)
        print(output)
        return 0
    except KeyboardInterrupt:
        print("已取消。", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"运行失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
