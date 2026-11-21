"""Claude Code status line that also saves plan usage for otomode's gate.

Claude Code pipes a JSON payload to the status line command on stdin; on Pro and
Max plans it carries `rate_limits` (five_hour, seven_day). This saves them to
~/.claude/otomode/usage.json (or $OTOMODE_USAGE_FILE) and prints a short line.

  "statusLine": {"type": "command", "command": "python ~/.claude/skills/otomode/scripts/statusline.py"}

If you already have a status line, call this from it with the same stdin.
"""
import json
import os
import sys
import tempfile
import time

PATH = os.environ.get("OTOMODE_USAGE_FILE") or os.path.join(
    os.path.expanduser("~"), ".claude", "otomode", "usage.json")


def window(rate_limits, name):
    w = (rate_limits or {}).get(name)
    if isinstance(w, dict) and w.get("used_percentage") is not None:
        return {"used_percentage": float(w["used_percentage"]), "resets_at": w.get("resets_at")}
    return None


def main():
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8-sig", errors="replace") or "{}")
    except ValueError:
        payload = {}
    rl = payload.get("rate_limits") or {}
    five, week = window(rl, "five_hour"), window(rl, "seven_day")
    if five or week:
        try:
            os.makedirs(os.path.dirname(PATH), exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=os.path.dirname(PATH), suffix=".tmp")
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump({"five_hour": five, "seven_day": week, "updated_at": time.time()}, f)
            os.replace(tmp, PATH)
        except OSError:
            pass
    parts = [(payload.get("model") or {}).get("display_name") or "Claude"]
    if five:
        parts.append(f"5h {five['used_percentage']:.0f}%")
    if week:
        parts.append(f"week {week['used_percentage']:.0f}%")
    sys.stdout.write(" | ".join(parts))


if __name__ == "__main__":
    main()
