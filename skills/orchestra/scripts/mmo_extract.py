"""Pull the final answer out of a lane's raw output. Exits non-zero when there is none.

    python mmo_extract.py kimi   RAW_FILE   # Kimi Code --output-format stream-json
    python mmo_extract.py claude RAW_FILE   # Claude Code -p --output-format json
"""
import json
import sys


def kimi(raw: str) -> str:
    # One JSON object per line; the answer is the last assistant message with text.
    last = ""
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        if ev.get("role") != "assistant":
            continue
        content = ev.get("content")
        if isinstance(content, list):
            content = "".join(p.get("text", "") for p in content if isinstance(p, dict))
        if isinstance(content, str) and content.strip():
            last = content
    return last


def claude(raw: str) -> str:
    data = json.loads(raw)
    if isinstance(data, list):  # some versions emit the event list
        data = data[-1] if data else {}
    if data.get("is_error") or data.get("permission_denials"):
        raise SystemExit("claude lane error: " + str(data.get("result") or data.get("permission_denials")))
    return data.get("result", "") or ""


def main() -> None:
    if len(sys.argv) != 3 or sys.argv[1] not in ("kimi", "claude"):
        raise SystemExit(__doc__)
    with open(sys.argv[2], encoding="utf-8", errors="replace") as f:
        raw = f.read()
    answer = kimi(raw) if sys.argv[1] == "kimi" else claude(raw)
    if not answer.strip():
        raise SystemExit("no answer in lane output")
    # Write UTF-8 bytes: a Windows console code page cannot encode every character a model emits.
    sys.stdout.buffer.write((answer.rstrip() + "\n").encode("utf-8"))


if __name__ == "__main__":
    main()
