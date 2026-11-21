"""Turn one headless Claude Code JSON result plus the grade into a scrubbed record.

    python collect.py ARM RUN RAW_JSON GRADE_JSON REPO_DIR OUT_JSON WALL_S EXIT
    python collect.py --scrub-file FILE REPO_DIR     scrub one file in place

Keeps cost, tokens, time, turns, per-model usage and permission denials (tool name
and a scrubbed input). Local paths and the user name are replaced before saving.
"""
import getpass
import json
import os
import re
import sys
from pathlib import Path


def scrubber(repo):
    pats = [str(Path(repo)), str(Path(repo)).replace("\\", "/"), os.path.expanduser("~"),
            os.path.expanduser("~").replace("\\", "/")]
    try:
        user = getpass.getuser()
    except Exception:
        user = None

    def scrub(s):
        for p in sorted(pats, key=len, reverse=True):
            s = s.replace(p, "<dir>")
        s = re.sub(r"/tmp/tmp\.\w+|[A-Za-z]:[\\/]+Users[\\/]+[^\\/\s\"']+", "<dir>", s)
        s = re.sub(r"/[a-z]/Users/[^/\s\"']+", "<dir>", s)
        if user:
            s = re.sub(re.escape(user), "<user>", s, flags=re.I)
        return s
    return scrub


def main():
    if sys.argv[1] == "--scrub-file":
        p = Path(sys.argv[2])
        p.write_text(scrubber(sys.argv[3])(p.read_text(encoding="utf-8", errors="replace")), encoding="utf-8")
        return
    arm, run, raw, grade, repo, out, wall, rc = sys.argv[1:9]
    scrub = scrubber(repo)
    try:
        d = json.loads(Path(raw).read_text(encoding="utf-8"))
    except Exception as e:  # headless run crashed or printed no JSON
        d = {"is_error": True, "result": f"no JSON result: {e}"}
    g = json.loads(Path(grade).read_text(encoding="utf-8"))
    u = d.get("usage") or {}
    rec = {
        "arm": arm, "run": int(run),
        "is_error": d.get("is_error"), "stop_reason": d.get("stop_reason"), "subtype": d.get("subtype"),
        "total_cost_usd": d.get("total_cost_usd"),
        "wall_s": int(wall), "exit": int(rc), "duration_ms": d.get("duration_ms"), "num_turns": d.get("num_turns"),
        "usage_main": {k: u.get(k) for k in ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")},
        "modelUsage": d.get("modelUsage"),
        "subagent_stats": d.get("subagent_stats"),
        "permission_denials": [{"tool": p.get("tool_name"), "input": scrub(json.dumps(p.get("tool_input")))[:300]}
                               for p in (d.get("permission_denials") or [])],
        "final_message": scrub(str(d.get("result") or ""))[-2000:],
        "grade": g,
    }
    Path(out).write_text(json.dumps(rec, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
