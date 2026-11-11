"""Build the bulk-classification task: 60 log lines, the rule set and the gold labels.

The lines are fixed (no randomness) so every run grades the same input.
"""
import re
from pathlib import Path

LINES = [
    "GET /api/users 200 12ms",
    "GET /api/users/42 404 3ms",
    "POST /api/orders 500 220ms",
    "worker-3 panic: nil map write",
    "cache warm: errors=0 hits=1200",
    "disk usage at 81 percent, warn threshold is 80",
    "PUT /api/orders/7 409 18ms",
    "auth: Error validating token for session 77",
    "GET /health 200 1ms",
    "db pool exhausted, fatal",
    "GET /static/app.js 304 2ms",
    "retrying upload (attempt 2 of 5)",
    "POST /api/login 401 9ms",
    "scheduler tick",
    "GET /api/reports 503 3001ms",
    "Warning: deprecated flag --legacy used",
    "kernel: FATAL machine check",
    "DELETE /api/users/9 204 7ms",
    "parser: no errors found",
    "GET /api/search 429 1ms",
    "error budget remaining 97 percent",
    "GET /favicon.ico 404 1ms",
    "PATCH /api/items/3 422 15ms",
    "backup finished in 812s",
    "tls handshake warn: weak cipher offered",
    "GET /api/export 502 60001ms",
    "warmup: 0 warnings",
    "runtime: goroutine panic recovered",
    "POST /api/upload 413 40ms",
    "GET / 200 5ms",
    "ERROR could not reach payment gateway",
    "metrics flushed",
    "GET /api/items 500 9ms",
    "config reloaded, warn: unknown key 'tz'",
    "GET /missing 404 2ms",
    "job 81 failed with error code 3",
    "user 5 logged in",
    "POST /api/pay 403 6ms",
    "OOM killer invoked, fatal for pid 4411",
    "GET /api/users 201 30ms",
    "cron: errorless run complete",
    "GET /admin 401 2ms",
    "fan speed nominal",
    "replication lag warn 4.2s",
    "GET /api/stream 504 30000ms",
    "Panic button pressed in UI test (simulated)",
    "GET /docs 301 1ms",
    "queue depth 0",
    "POST /api/orders 400 11ms",
    "certificate expires in 6 days (warn)",
    "GET /api/v2/x 404 4ms",
    "shutdown requested by operator",
    "GET /api/slow 500 1200ms",
    "index rebuilt with 0 errors",
    "POST /api/retry 408 5000ms",
    "ingest: error rate 0.01 percent",
    "GET /ok 200 1ms",
    "panicked at 'index out of bounds'",
    "warn",
    "GET /api/teapot 418 1ms",
]

RULES = """Label every line with exactly one of CRITICAL, ERROR, WARN, INFO.
Apply the first rule that matches, top to bottom:
1. CRITICAL if the line contains the whole word "panic" or "fatal" (any case).
   Whole word means "panic" matches, "panicked" does not.
2. ERROR if it contains the whole word "error" (any case), or an HTTP status from 500 to 599.
   "errors", "errorless" are not the whole word "error".
3. WARN if it contains the whole word "warn" or "warning" (any case),
   or an HTTP status from 400 to 499 other than 404.
4. INFO otherwise (including 404).
An HTTP status is a 3-digit number right after a request path, as in "GET /x 503 2ms"."""

STATUS = re.compile(r"^(GET|POST|PUT|PATCH|DELETE) \S+ (\d{3}) ")


def word(line, *ws):
    return any(re.search(rf"\b{w}\b", line, re.IGNORECASE) for w in ws)


def label(line):
    m = STATUS.match(line)
    code = int(m.group(2)) if m else None
    if word(line, "panic", "fatal"):
        return "CRITICAL"
    if word(line, "error") or (code is not None and 500 <= code <= 599):
        return "ERROR"
    if word(line, "warn", "warning") or (code is not None and 400 <= code <= 499 and code != 404):
        return "WARN"
    return "INFO"


def main():
    here = Path(__file__).parent
    numbered = "\n".join(f"{i}\t{line}" for i, line in enumerate(LINES, 1))
    (here / "brief.md").write_text(
        RULES
        + "\n\nReply with CSV only: a header line `line,label`, then one row per line, in order.\n"
        + "No other text.\n\nLines (number TAB text):\n\n"
        + numbered + "\n",
        encoding="utf-8",
    )
    (here / "gold.csv").write_text(
        "line,label\n" + "".join(f"{i},{label(l)}\n" for i, l in enumerate(LINES, 1)), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
