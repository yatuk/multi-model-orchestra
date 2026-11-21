"""otomode helper: state switch, permission hook and usage readout.

  python otomode.py on --project DIR --hours N [--session ID]
  python otomode.py off
  python otomode.py status
  python otomode.py gate [--percent P --reset ISO]
  python otomode.py usage
  python otomode.py install | uninstall   (register the hook in ~/.claude/settings.json)
  python otomode.py hook          (Claude Code hook; reads the event JSON on stdin)

State lives in ~/.claude/otomode/state.json. The hook does nothing unless that
file exists, so it can stay registered in settings.json permanently.
"""
import os
import sys

STATE_DIR = os.path.join(os.path.expanduser("~"), ".claude", "otomode")
STATE_FILE = os.path.join(STATE_DIR, "state.json")


def _fast_exit_if_off():
    # Hook fast path: no imports beyond os/sys when otomode is off.
    if len(sys.argv) > 1 and sys.argv[1] == "hook" and not os.path.exists(STATE_FILE):
        sys.exit(0)


_fast_exit_if_off()

import json  # noqa: E402
import re  # noqa: E402
import time  # noqa: E402
from datetime import datetime  # noqa: E402

# Commands otomode never runs: delete, deploy, send. Checked on Bash/PowerShell.
# C = the word is in command position (start, after ; & | ( or sudo), so
# `grep mail` or `cat deploy.md` stay allowed.
C = r"(^|[;&|(]\s*|\bsudo\s+|\bxargs\s+)"
BLOCKED_COMMANDS = [
    (C + r"rm\s", "delete (rm)"),
    (r"\bgit\s+rm\s", "delete (git rm)"),
    (C + r"(rmdir|del|erase|shred|unlink|rd)\s", "delete"),
    (r"\b(Remove-Item|Clear-Content)\b", "delete (Remove-Item)"),
    (r"git\s+(push|send-email)\b", "git push"),
    (r"git\s+branch\s+.*-[dD]\b", "delete branch"),
    (r"git\s+(clean|worktree\s+remove|worktree\s+prune|stash\s+(drop|clear))\b", "delete (git)"),
    (r"git\s+reset\s+--hard", "git reset --hard"),
    (r"git\s+checkout\s+--\s", "discard changes"),
    (r"git\s+restore\b(?!.*--staged)", "discard changes"),
    (r"git\s+tag\s+.*-d\b", "delete tag"),
    (r"\bgh\s+(pr\s+(create|merge|comment|close|review)|issue\s+(create|comment|close)|release|repo\s+delete|api\b)", "GitHub write"),
    (C + r"(kubectl|helm|terraform|ansible-playbook|pulumi|vercel|netlify|flyctl|fly|az|aws|gcloud)\s", "deploy"),
    (r"docker\s+(push|compose\s+up|run|rm|rmi|system\s+prune|volume\s+rm)", "docker deploy/delete"),
    (r"\b(npm|pnpm|yarn)\s+publish\b|\bcargo\s+publish\b|\btwine\s+upload\b", "publish"),
    (C + r"(scp|rsync|ssh|sftp)\s", "remote host"),
    (r"\b(curl|wget|Invoke-WebRequest|Invoke-RestMethod|iwr|irm)\b.*(-X\s*(POST|PUT|DELETE|PATCH)|--data|-d\s|-F\s|-Method\s+(Post|Put|Delete|Patch))", "outbound write request"),
    (C + r"(sendmail|mail|mutt)\s|\bSend-MailMessage\b", "send mail"),
    (C + r"shutdown\s|\b(Restart-Computer|Stop-Computer)\b", "machine control"),
]

# MCP tools whose name says they send, post, delete or deploy.
BLOCKED_TOOL_WORDS = re.compile(
    r"(^|_|-)(send|post|reply|publish|delete|remove|trash|deploy|create_event|update_event|"
    r"respond_to_event|submit|merge|set_auto_merge|move_to_cloud|stop_session|renew|reserve|"
    r"push|upload|file_upload|form_input)(_|-|$)",
    re.I,
)
# Tools that only ask the user something.
ASK_TOOLS = {"AskUserQuestion", "ExitPlanMode", "EnterPlanMode"}


def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def save_state(state):
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, STATE_FILE)


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def short(value, limit=600):
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    text = text.replace("\r", " ")
    return text if len(text) <= limit else text[:limit] + " ..."


def log_question(state, kind, tool, detail):
    path = os.path.join(state["project"], "QUESTIONS.md")
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8") as f:
        if new:
            f.write("# Otomode questions\n\nDenied while you were away. Answer these when otomode ends.\n\n")
        f.write(f"## {now()} · {kind} · `{tool}`\n\n{detail}\n\n")
    state["denied"] = state.get("denied", 0) + 1
    save_state(state)


def describe_ask(tool_input):
    qs = tool_input.get("questions")
    if not isinstance(qs, list):
        return "```\n" + short(tool_input) + "\n```"
    lines = []
    for q in qs:
        lines.append(f"- **{q.get('question', '?')}**")
        for o in q.get("options") or []:
            lines.append(f"  - {o.get('label', '')}: {o.get('description', '')}")
    return "\n".join(lines)


def blocked_reason(tool, tool_input):
    if tool in ("Bash", "PowerShell"):
        cmd = str(tool_input.get("command", ""))
        for pattern, label in BLOCKED_COMMANDS:
            if re.search(pattern, cmd, re.I):
                return label
    elif tool.startswith("mcp__") and BLOCKED_TOOL_WORDS.search(tool.split("__")[-1]):
        return "sends, deletes or deploys"
    return None


def emit(event, reason):
    if event == "PermissionRequest":
        out = {"hookSpecificOutput": {"hookEventName": "PermissionRequest",
                                      "decision": {"behavior": "deny", "message": reason}}}
    else:
        out = {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                      "permissionDecision": "deny",
                                      "permissionDecisionReason": reason}}
    sys.stdout.write(json.dumps(out))


def hook():
    state = load_state()
    if not state:
        return
    try:
        event = json.loads(sys.stdin.buffer.read().decode("utf-8-sig", errors="replace") or "{}")
    except ValueError:
        return
    sid = state.get("session_id")
    if sid and event.get("session_id") and event["session_id"] != sid:
        return  # another session: not ours
    name = event.get("hook_event_name", "")
    tool = event.get("tool_name", "")
    tool_input = event.get("tool_input") or {}
    tail = (" Otomode is on and the user is away: do not wait. It is logged in QUESTIONS.md. "
            "Pick the safe default, work around it, or mark the task blocked and move on.")

    if tool in ASK_TOOLS:
        log_question(state, "question", tool, describe_ask(tool_input))
        emit(name, f"Question not shown: {tool}.{tail}")
        return
    label = blocked_reason(tool, tool_input)
    if label:
        log_question(state, f"blocked ({label})", tool, "```\n" + short(tool_input) + "\n```")
        emit(name, f"Blocked by otomode rule: never {label}.{tail}")
        return
    if name == "PermissionRequest":
        log_question(state, "permission", tool, "```\n" + short(tool_input) + "\n```")
        emit(name, f"Permission prompt denied for {tool}.{tail}")


USAGE_FILE = os.environ.get("OTOMODE_USAGE_FILE") or os.path.join(STATE_DIR, "usage.json")


def read_usage():
    """Plan usage saved by statusline.py (Claude Code passes rate_limits to the status line)."""
    try:
        with open(USAGE_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {"status": "unavailable", "note": "no usage file: install statusline.py, or pass --percent/--reset to gate"}
    windows = []
    for key in ("five_hour", "seven_day"):
        w = data.get(key)
        if isinstance(w, dict) and w.get("used_percentage") is not None:
            reset = w.get("resets_at")
            if isinstance(reset, (int, float)):
                reset = datetime.fromtimestamp(reset).strftime("%Y-%m-%d %H:%M")
            windows.append({"window": key, "percent": round(float(w["used_percentage"])), "resets_at": reset})
    age = int(time.time() - float(data.get("updated_at") or 0))
    top = max(windows, key=lambda w: w["percent"]) if windows else None
    return {"status": "ok" if windows else "unavailable", "windows": windows,
            "max_percent": top["percent"] if top else None,
            "binding_reset": top["resets_at"] if top else None,
            "age_seconds": age, "stale": age > 900}


def parse_when(value):
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value))
    text = str(value).replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    return dt.astimezone().replace(tzinfo=None) if dt.tzinfo else dt


def gate(opts):
    """Decide whether a new task may start. 85% of any window stops new work."""
    limit = float(opts.get("--limit", "85"))
    if "--percent" in opts:  # numbers from get_usage (desktop)
        percent = float(opts["--percent"])
        reset = parse_when(opts.get("--reset"))
        source = "get_usage"
    else:
        u = read_usage()
        if u["status"] != "ok" or u.get("stale"):
            return {"decision": "unknown", "source": "statusline",
                    "note": "usage unknown or stale: call get_usage and pass --percent/--reset, "
                            "else continue one task at a time and check again"}
        percent, reset, source = float(u["max_percent"]), parse_when(u["binding_reset"]), "statusline"
    if reset and reset < datetime.now():
        return {"decision": "go", "source": source, "percent": 0, "note": "window already reset"}
    out = {"source": source, "percent": percent, "limit": limit,
           "reset": reset.strftime("%Y-%m-%d %H:%M") if reset else None}
    if percent < limit:
        out["decision"] = "go"
        return out
    out["decision"] = "stop"
    if reset:
        at = datetime.fromtimestamp(reset.timestamp() + 4 * 60)
        out["resume_cron"] = f"{at.minute} {at.hour} {at.day} {at.month} *"
        out["resume_at"] = at.strftime("%Y-%m-%d %H:%M")
    state = load_state()
    if state and state.get("ends") and reset and reset.strftime("%Y-%m-%d %H:%M") > state["ends"]:
        out["note"] = "reset is after the run ends: write the summary instead of resuming"
    return out


HOOK_EVENTS = {
    "PermissionRequest": "*",
    "PreToolUse": "AskUserQuestion|ExitPlanMode|EnterPlanMode|Bash|PowerShell|mcp__.*",
}


def settings_path():
    return os.path.join(os.path.expanduser("~"), ".claude", "settings.json")


def hook_command():
    script = os.path.abspath(__file__).replace("\\", "/")
    exe = sys.executable.replace("\\", "/")
    return f'"{exe}" "{script}" hook'


def install(remove=False):
    path = settings_path()
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    hooks = data.setdefault("hooks", {})
    for event, matcher in HOOK_EVENTS.items():
        entries = [e for e in hooks.get(event, [])
                   if not any("otomode.py" in h.get("command", "") for h in e.get("hooks", []))]
        if not remove:
            entries.append({"matcher": matcher,
                            "hooks": [{"type": "command", "command": hook_command(), "timeout": 10}]})
        if entries:
            hooks[event] = entries
        else:
            hooks.pop(event, None)
    if not hooks:
        data.pop("hooks", None)
    if os.path.exists(path):
        os.replace(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(("removed from " if remove else "installed in ") + path + " (previous copy: settings.json.bak)")


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "status"
    if cmd == "hook":
        hook()
    elif cmd in ("install", "uninstall"):
        install(remove=cmd == "uninstall")
    elif cmd == "gate":
        print(json.dumps(gate(dict(zip(args[1::2], args[2::2]))), indent=2))
    elif cmd == "on":
        opts = dict(zip(args[1::2], args[2::2]))
        project = os.path.abspath(opts.get("--project", os.getcwd()))
        hours = float(opts.get("--hours", "6"))
        state = {"project": project, "hours": hours, "started": now(),
                 "ends": datetime.fromtimestamp(time.time() + hours * 3600).strftime("%Y-%m-%d %H:%M"),
                 "session_id": opts.get("--session") or os.environ.get("CLAUDE_CODE_SESSION_ID") or None,
                 "denied": 0}
        save_state(state)
        print(json.dumps(state, indent=2))
    elif cmd == "off":
        state = load_state()
        if os.path.exists(STATE_FILE):
            os.replace(STATE_FILE, os.path.join(STATE_DIR, "last-run.json"))
        print(json.dumps({"off": True, "was": state}, indent=2))
    elif cmd == "status":
        state = load_state()
        print(json.dumps({"on": bool(state), "state": state, "usage": read_usage()}, indent=2))
    elif cmd == "usage":
        print(json.dumps(read_usage(), indent=2))
    else:
        sys.exit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
