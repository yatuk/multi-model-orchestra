#!/usr/bin/env python3
"""Loop detector for lanes that stream JSON lines (used by mmo-run --loop N).

    mmo_loop.py N FILE     exit 10 when the same action or error line appears N times in a row
                           in FILE (0 otherwise); N below 2 never fires
    mmo_loop.py norm       read one line on stdin; print its normalized form, or nothing when the
                           line is not an action or error

Conservative on purpose: only lines that parse as JSON objects count, and only when they name a
tool call or an error. Text and thinking events between two identical actions do not reset the
count; a different action or error does. Plain-text output is never judged.
"""
import json
import re
import sys

ACTION_KEYS = ("tool", "tool_name", "toolName", "tool_call", "toolCall", "tool_calls", "function_call")
ACTION_TYPES = ("tool_use", "tool_call", "function_call", "error")
# Keys whose value changes on every event without the action changing.
VOLATILE = re.compile(
    r"^(id|uuid|ts|time|timestamp|date|seq|sequence|index|idx|created|elapsed|latency|duration|"
    r".*_id|.*Id|.*_at|.*_ms|.*_ts|.*_seconds|duration.*|elapsed.*|timestamp.*)$"
)


def _strip(value):
    if isinstance(value, dict):
        return {k: _strip(v) for k, v in value.items() if not VOLATILE.match(k)}
    if isinstance(value, list):
        return [_strip(v) for v in value]
    return value


def _is_action(obj):
    if any(obj.get(k) for k in ACTION_KEYS):
        return True
    if obj.get("name") and any(k in obj for k in ("input", "arguments", "args")):
        return True
    if obj.get("error"):
        return True
    return obj.get("type") in ACTION_TYPES


def _blocks(obj):
    """tool_use blocks nested in message.content, as Claude-style streams carry them."""
    msg = obj.get("message")
    content = (msg.get("content") if isinstance(msg, dict) else None) or obj.get("content")
    if isinstance(content, list):
        return [b for b in content if isinstance(b, dict) and b.get("type") == "tool_use"]
    return []


def normalize(line):
    """Return a comparable string for an action or error line, else None."""
    line = line.strip()
    if not line.startswith("{"):
        return None
    try:
        obj = json.loads(line)
    except ValueError:
        return None
    if not isinstance(obj, dict):
        return None
    blocks = _blocks(obj)
    if blocks:
        return json.dumps(_strip(blocks), sort_keys=True, ensure_ascii=False)
    if not _is_action(obj):
        return None
    return json.dumps(_strip(obj), sort_keys=True, ensure_ascii=False)


def looping(lines, n):
    if n < 2:
        return False
    last, count = None, 0
    for line in lines:
        key = normalize(line)
        if key is None:
            continue
        if key == last:
            count += 1
        else:
            last, count = key, 1
        if count >= n:
            return True
    return False


def main(argv):
    if len(argv) == 2 and argv[1] == "norm":
        key = normalize(sys.stdin.readline())
        if key is not None:
            print(key)
        return 0
    if len(argv) != 3 or not argv[1].isdigit():
        print("usage: mmo_loop.py N FILE | mmo_loop.py norm", file=sys.stderr)
        return 2
    try:
        with open(argv[2], encoding="utf-8", errors="replace") as f:
            return 10 if looping(f, int(argv[1])) else 0
    except OSError:
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
