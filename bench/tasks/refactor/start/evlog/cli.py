"""Command line: python -m evlog.cli FILE [--min-level L] [--strict] [--utc-offset M] [--top N]

Prints a summary of FILE:
    total 5
    DEBUG 0
    INFO 3
    WARN 1
    ERROR 1
    first 2026-03-01T10:00:00
    last 2026-03-01T11:30:00
and, with --top N, one line per frequent message: `top COUNT MESSAGE`.
A ParseError prints `error: <message>` and returns 2. Success returns 0.
"""
import argparse
import sys

from .model import LEVELS, ParseError
from .summary import summarize, top_messages


def main(argv=None, out=None):
    out = out or sys.stdout
    ap = argparse.ArgumentParser(prog="evlog")
    ap.add_argument("file")
    ap.add_argument("--min-level", default="DEBUG", choices=LEVELS)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--utc-offset", type=int, default=0)
    ap.add_argument("--top", type=int, default=0)
    args = ap.parse_args(argv)
    with open(args.file, encoding="utf-8") as f:
        lines = f.readlines()
    try:
        s = summarize(lines, args.min_level, args.strict, args.utc_offset)
        top = top_messages(lines, args.top, args.min_level, args.strict, args.utc_offset) if args.top else []
    except ParseError as err:
        print(f"error: {err}", file=out)
        return 2
    print(f"total {s['total']}", file=out)
    for name in LEVELS:
        print(f"{name} {s['by_level'][name]}", file=out)
    print(f"first {s['first']}", file=out)
    print(f"last {s['last']}", file=out)
    for message, count in top:
        print(f"top {count} {message}", file=out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
