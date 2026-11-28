"""otomode helper: state switch, permission hook and usage readout.

  python otomode.py on --project DIR --hours N [--session ID | --all-sessions] [--force]
  python otomode.py off
  python otomode.py status
  python otomode.py log "<text>" [--project DIR]   (timestamped line in the OTOMODE.md log)
  python otomode.py gate [--percent P --reset ISO]
  python otomode.py usage
  python otomode.py merged T<n> --quick-exit CODE   (after each cherry-pick: the quick check's exit code)
  python otomode.py cron [--watchdog ID] [--resume ID]   (record the cron job ids in the state)
  python otomode.py lane T<n> <lane> [--log FILE]   (record a Claude lane launch for the scoreboard)
  python otomode.py score [--log FILE]   (per-lane first-try pass counts from .otomode/lanes.jsonl)
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
import subprocess  # noqa: E402
import time  # noqa: E402
from datetime import datetime  # noqa: E402

# Commands otomode never runs (delete, deploy, push, send) are judged in
# cmdscan.py: a Bash line is parsed and only the commands that would run are
# checked (not text inside heredocs, quotes or commit messages); PowerShell
# uses whole-text regex rules.

# MCP tools whose name says they send, post, delete or deploy.
BLOCKED_TOOL_WORDS = re.compile(
    r"(^|_|-)(send|post|reply|publish|delete|remove|trash|deploy|create_event|update_event|"
    r"respond_to_event|submit|merge|set_auto_merge|move_to_cloud|stop_session|renew|reserve|"
    r"save_registration|kaydet|not_doldur|push|upload|file_upload|form_input)(_|-|$)",
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


# Denial classes. off_limits: a delete/push/deploy/send rule fired (working as designed).
# question: AskUserQuestion or plan mode. allowlist_gap: a plain permission prompt for something
# the start round did not pre-approve; these are the ones worth an allow rule next time.
CLASSES = ("off_limits", "question", "allowlist_gap")
MAX_GAPS = 20


def _rule(tool, words):
    """`Tool(first word [subcommand]:*)` for one simple command's words."""
    words = [w.replace(chr(0), "") for w in words]  # cmdscan marks unknown expansions with NUL
    while words and re.match(r"^\w+=", words[0]):  # leading VAR=value assignments
        words.pop(0)
    if not words:
        return None
    # Two words when the second is a subcommand (go test, npm run, git -C is one word).
    key = words[0] if len(words) < 2 or not re.match(r"^[a-z][\w.-]*$", words[1]) else " ".join(words[:2])
    return f"{tool}({key[:80]}:*)"


def gap_key(tool, tool_input):
    """Short allow-rule suggestion for the first command: the tool, or the shell's first word(s)."""
    if tool not in ("Bash", "PowerShell"):
        return tool
    return _rule(tool, str(tool_input.get("command", "")).split()) or tool


def gap_rules(tool, tool_input):
    """One suggested rule per command segment. Claude Code matches each segment of a compound command
    (`a; b`, `a && b`, pipes, loop bodies) against the allow rules and needs all of them, so naming only
    the first word points at the wrong cause. The hook does not read Claude Code's allow rules, so it
    cannot tell which segments are already covered: it lists every segment."""
    if tool != "Bash":
        return [gap_key(tool, tool_input)]
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import cmdscan  # next to this script
    cmd = str(tool_input.get("command", ""))
    try:
        argvs, _ = cmdscan.parse(cmd)
    except cmdscan.Unsure:
        return [gap_key(tool, tool_input)]
    rules = []
    for argv in argvs:
        argv = list(argv)
        if argv and argv[0] in ("for", "select", "case", "in", "function"):
            continue  # loop or case header: no command runs here
        while argv and (argv[0] in cmdscan.KEYWORDS or cmdscan.ASSIGN.match(argv[0])):
            argv.pop(0)  # `do git ...`, `then make`, `VAR=1 cmd`
        rule = _rule(tool, argv) if argv else None
        if rule and rule not in rules:
            rules.append(rule)
    return rules or [gap_key(tool, tool_input)]


COMPOUND_NOTE = ("Compound command: Claude Code needs every segment allowed. Suggested rules, one per "
                 "segment (the hook cannot tell which are already allowed, so all are listed): ")


def log_question(state, cls, kind, tool, detail, gap=None):
    gaps_new = [gap] if isinstance(gap, str) else list(gap or [])
    if len(gaps_new) > 1:
        detail += "\n\n" + COMPOUND_NOTE + ", ".join(f"`{g}`" for g in gaps_new)
    path = os.path.join(state["project"], "QUESTIONS.md")
    new = not os.path.exists(path)
    with open(path, "a", encoding="utf-8") as f:
        if new:
            f.write("# Otomode questions\n\nDenied while you were away. Answer these when otomode ends.\n\n")
        f.write(f"## {now()} · {cls} · {kind} · `{tool}`\n\n{detail}\n\n")
    state["denied"] = state.get("denied", 0) + 1
    counts = state.setdefault("denials", {c: 0 for c in CLASSES})
    counts[cls] = counts.get(cls, 0) + 1
    gaps = state.setdefault("allowlist_gaps", [])
    for g in gaps_new:
        if g not in gaps and len(gaps) < MAX_GAPS:
            gaps.append(g)
    save_state(state)


def denial_report(state):
    state = state or {}
    counts = {c: 0 for c in CLASSES}
    counts.update(state.get("denials") or {})
    return {"denials_by_class": counts, "suggested_allow_rules": state.get("allowlist_gaps", [])}


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
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import cmdscan  # next to this script; only loaded while otomode is on
        cmd = str(tool_input.get("command", ""))
        return cmdscan.bash_reason(cmd) if tool == "Bash" else cmdscan.powershell_reason(cmd)
    if tool.startswith("mcp__") and BLOCKED_TOOL_WORDS.search(tool.split("__")[-1]):
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
        log_question(state, "question", "question", tool, describe_ask(tool_input))
        emit(name, f"Question not shown: {tool}.{tail}")
        return
    label = blocked_reason(tool, tool_input)
    if label:
        if tool in ("Bash", "PowerShell"):  # listed as "cleanup left for you" at the end
            state.setdefault("blocked", []).append(
                {"time": now(), "tool": tool, "why": label, "command": short(tool_input.get("command", ""), 400)})
            del state["blocked"][:-50]
        log_question(state, "off_limits", f"blocked ({label})", tool, "```\n" + short(tool_input) + "\n```")
        emit(name, f"Blocked by otomode rule: never {label}.{tail}")
        return
    if name == "PermissionRequest":
        log_question(state, "allowlist_gap", "permission", tool, "```\n" + short(tool_input) + "\n```",
                     gap=gap_rules(tool, tool_input))
        emit(name, f"Permission prompt denied for {tool}.{tail}")


STALE_SECONDS = 900
USAGE_FILE = os.environ.get("OTOMODE_USAGE_FILE") or os.path.join(STATE_DIR, "usage.json")


def read_usage():
    """Plan usage saved by statusline.py (Claude Code passes rate_limits to the status line)."""
    try:
        with open(USAGE_FILE, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {"status": "unavailable", "note": f"no usage file at {USAGE_FILE}: install statusline.py, or pass --percent/--reset to gate"}
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
            "age_seconds": age, "stale": age > STALE_SECONDS}


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
            if u["status"] != "ok":  # say why, so print mode (no statusline, no get_usage) is understood
                why = u.get("note") or f"no usable window in {USAGE_FILE}"
            else:
                why = (f"usage file {USAGE_FILE} is older than {STALE_SECONDS // 60} minutes "
                       f"({u['age_seconds'] // 60} minutes old)")
            return {"decision": "unknown", "source": "statusline", "why": why,
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


def log_line(text, project=None):
    """Append `- HH:MM text` to the Log section of OTOMODE.md; the time comes from the clock."""
    state = load_state() or {}
    project = project or state.get("project") or os.getcwd()
    path = os.path.join(project, "OTOMODE.md")
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except FileNotFoundError:
        lines = ["# Otomode run"]
    entry = f"- {datetime.now().strftime('%H:%M')} {' '.join(text.split())}"
    head = next((k for k, x in enumerate(lines) if x.strip().lower() == "## log"), None)
    if head is None:
        lines += ["", "## Log", entry]
    else:
        k = head + 1
        while k < len(lines) and not lines[k].startswith("## "):
            k += 1
        while k > head + 1 and not lines[k - 1].strip():
            k -= 1
        lines.insert(k, entry)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    return entry


def lanes_log(opts):
    state = load_state()
    if state is None:  # after `off` the state moved to last-run.json; the end report still scores
        try:
            with open(os.path.join(STATE_DIR, "last-run.json"), encoding="utf-8") as f:
                state = json.load(f)
        except (OSError, ValueError):
            state = {}
    project = (state or {}).get("project") or os.getcwd()
    return opts.get("--log") or os.path.join(project, ".otomode", "lanes.jsonl")


def record_lane(task, lane, path):
    """Claude sub-agents write no JSONL line of their own; the conductor records the launch."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"ts": now(), "kind": "lane", "task": task, "lane": lane}) + "\n")


# mmo-run statuses that are the lane's own failure. base (stale worktree), model, limit and auth
# are not tries: the conductor fixes the setup and starts again.
LANE_FAILURES = ("failed", "timeout", "stalled", "empty")


def score(path):
    """Per lane: how many tasks it was tried on and how often its first check passed.

    mmo-run writes kind=run lines (provider/model), `otomode.py lane` writes kind=lane, mmo-check
    writes kind=check. A check counts for the lane last started on the same task; only the first
    outcome per task and lane counts. A lane run that failed or timed out is a first-try failure.
    """
    current, seen, out = {}, set(), {}
    try:
        with open(path, encoding="utf-8") as f:
            rows = [json.loads(x) for x in f if x.strip()]
    except OSError:
        rows = []
    except ValueError as e:
        return {"error": f"bad line in {path}: {e}"}

    def tally(task, lane, passed):
        if (task, lane) in seen:
            return
        seen.add((task, lane))
        s = out.setdefault(lane, {"tasks": 0, "first_try_pass": 0})
        s["tasks"] += 1
        s["first_try_pass"] += int(passed)

    for r in rows:
        task, kind = r.get("task") or "?", r.get("kind")
        if kind == "lane":
            current[task] = r.get("lane") or "?"
        elif kind == "run":
            current[task] = f"{r.get('provider', '?')} {r.get('model') or 'default'}"  # same form as mmo-roster
            if r.get("status") in LANE_FAILURES:
                tally(task, current[task], False)
        elif kind == "check":
            tally(task, current.get(task, "?"), r.get("status") == "pass")
    return {"log": path, "lanes": out}


def parse_opts(args, flags=()):
    """`--key value` pairs and bare flags; anything else is ignored."""
    opts, i = {}, 0
    while i < len(args):
        if args[i] in flags:
            opts[args[i]] = True
            i += 1
        elif args[i].startswith("--") and i + 1 < len(args):
            opts[args[i]] = args[i + 1]
            i += 2
        else:
            i += 1
    return opts


LANE_TIERS = re.compile(r"\b(?:strong|middle|cheap|bulk)\s*=\s*([^·\n]*)")


def plan_lanes_problem(project):
    """Why OTOMODE.md cannot start a run (no Lanes: line, or it names no lane), else None.

    The lineup is the start round's announcement; a Lanes: line naming a lane is the trace that the
    probe and the lineup happened. Text alone did not make a conductor run them."""
    try:
        with open(os.path.join(project, "OTOMODE.md"), encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return f"no OTOMODE.md in {project}"
    line = next((x for x in text.splitlines() if x.strip().startswith("Lanes:")), None)
    if line is None:
        return "OTOMODE.md has no Lanes: line"
    named = [v.strip() for v in LANE_TIERS.findall(line)]
    named = [v for v in named if v and not re.match(r"(?i)^(<|none\b|nothing\b|-)", v)]
    return None if named else "the Lanes: line names no lane"


def git_exclude(project, lines=(".otomode/", "QUESTIONS.md")):
    """Add the run's own files to the repo's .git/info/exclude (a plain script write: Claude Code
    refuses a model edit of that file). Append only what is missing; never raise."""
    try:
        r = subprocess.run(["git", "-C", project, "rev-parse", "--git-path", "info/exclude"],
                           capture_output=True, text=True, timeout=20)
        if r.returncode != 0 or not r.stdout.strip():
            return {"path": None, "added": [], "error": (r.stderr.strip() or "not a git repository")[:200]}
        path = r.stdout.strip()
        if not os.path.isabs(path):  # relative to the project; a worktree has a .git file, git knows the real dir
            path = os.path.join(project, path)
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except FileNotFoundError:
            text = ""
        have = {x.strip() for x in text.splitlines()}
        missing = [x for x in lines if x not in have]
        if missing:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "a", encoding="utf-8", newline="\n") as f:
                f.write(("" if not text or text.endswith("\n") else "\n") + "\n".join(missing) + "\n")
        return {"path": path, "added": missing, "error": None}
    except (OSError, subprocess.SubprocessError) as e:
        return {"path": None, "added": [], "error": str(e)[:200]}


def turn_on(args):
    """`on`: returns (exit code, output). Refuses without a lineup trace or a session binding."""
    opts = parse_opts(args, flags=("--force", "--all-sessions"))
    project = os.path.abspath(opts.get("--project", os.getcwd()))
    session = opts.get("--session") or os.environ.get("CLAUDE_CODE_SESSION_ID") or None
    if not session and not opts.get("--all-sessions"):
        return 2, {"on": False, "error": "no session id (no --session, no CLAUDE_CODE_SESSION_ID): the hook "
                   "would deny in EVERY session on this machine. Pass --session ID, or --all-sessions if that "
                   "is what you want."}
    problem = plan_lanes_problem(project)
    if problem and not opts.get("--force"):
        return 2, {"on": False, "error": f"{problem}. Run mmo-roster probe and lineup, show the lineup to the "
                   "user in the start round, and write the Lanes: line (or pass --force)."}
    hours = float(opts.get("--hours", "6"))
    state = {"project": project, "hours": hours, "started": now(),
             "ends": datetime.fromtimestamp(time.time() + hours * 3600).strftime("%Y-%m-%d %H:%M"),
             "session_id": session, "denied": 0, "denials": {c: 0 for c in CLASSES}, "allowlist_gaps": []}
    save_state(state)
    return 0, {**state, "git_exclude": git_exclude(project),
               "forced_without_lanes": bool(problem),
               "reminder": "The lineup (mmo-roster lineup) must have been shown to the user in the start round."}


def done_tasks(project):
    """Number of task rows with status done in OTOMODE.md, or None when unreadable."""
    try:
        with open(os.path.join(project, "OTOMODE.md"), encoding="utf-8") as f:
            rows = [[c.strip() for c in x.strip().strip("|").split("|")] for x in f if x.lstrip().startswith("|")]
    except OSError:
        return None
    return sum(1 for r in rows if re.match(r"^T\d+$", r[0]) and "done" in r[1:])


def quick_summary(state):
    """The quick check's record: how many merged tasks had it run, and how many of those passed."""
    merged = (state or {}).get("merged") or {}
    done = done_tasks(state["project"]) if state and state.get("project") else None
    total = max(done if done is not None else 0, len(merged))
    failed = sorted(t for t, c in merged.items() if c != 0)
    text = f"quick check after merge: {len(merged)} of {total} tasks"
    if failed:
        text += " (failed: " + ", ".join(failed) + ")"
    return {"text": text, "checked": len(merged), "tasks": total, "failed": failed}


def record_merged(task, code):
    state = load_state()
    if not state:
        return 2, {"error": "otomode is off: nothing recorded"}
    state.setdefault("merged", {})[task] = code
    save_state(state)
    line = log_line(f"{task} merged, quick check exit={code} ({'pass' if code == 0 else 'FAIL'})", state["project"])
    return 0, {"logged": line, **quick_summary(state)}


def record_cron(opts):
    state = load_state()
    if not state:
        return 2, {"error": "otomode is off: nothing recorded"}
    crons = state.setdefault("crons", {})
    for flag, key in (("--watchdog", "watchdog"), ("--resume", "resume")):
        if flag in opts:
            if opts[flag].lower() == "none":
                crons.pop(key, None)
            else:
                crons[key] = opts[flag]
    save_state(state)
    return 0, {"crons": crons}


def bound_to(state):
    if not state:
        return None
    sid = state.get("session_id")
    return sid[:8] if sid else "all sessions"


def main():
    args = sys.argv[1:]
    cmd = args[0] if args else "status"
    if cmd == "hook":
        hook()
    elif cmd == "log":
        rest, project = args[1:], None
        if "--project" in rest:
            k = rest.index("--project")
            project = rest[k + 1] if k + 1 < len(rest) else None
            rest = rest[:k] + rest[k + 2:]
        if not rest:
            sys.exit('usage: otomode.py log "<text>" [--project DIR]')
        print(log_line(" ".join(rest), project))
    elif cmd in ("install", "uninstall"):
        install(remove=cmd == "uninstall")
    elif cmd == "gate":
        print(json.dumps(gate(dict(zip(args[1::2], args[2::2]))), indent=2))
    elif cmd == "on":
        code, out = turn_on(args[1:])
        print(json.dumps(out, indent=2))
        sys.exit(code)
    elif cmd == "merged":
        if len(args) < 2 or "--quick-exit" not in args:
            sys.exit("usage: otomode.py merged T<n> --quick-exit <code>")
        try:
            code = int(args[args.index("--quick-exit") + 1])
        except (ValueError, IndexError):
            sys.exit("--quick-exit takes the quick check's exit code (a number)")
        rc, out = record_merged(args[1], code)
        print(json.dumps(out, indent=2))
        sys.exit(rc)
    elif cmd == "cron":
        rc, out = record_cron(parse_opts(args[1:]))
        print(json.dumps(out, indent=2))
        sys.exit(rc)
    elif cmd == "off":
        state = load_state()
        if os.path.exists(STATE_FILE):
            os.replace(STATE_FILE, os.path.join(STATE_DIR, "last-run.json"))
        cleanup = [b["command"] for b in (state or {}).get("blocked", [])]
        quick = quick_summary(state)["text"] if state else None
        print(json.dumps({"off": True, **denial_report(state), "quick_check": quick,
                          "cleanup_left_for_you": cleanup, "was": state}, indent=2))
    elif cmd == "status":
        state = load_state()
        out = {"on": bool(state), "bound_to_session": bound_to(state), **denial_report(state)}
        if state:
            out.update(crons=state.get("crons") or {}, quick_check=quick_summary(state)["text"])
        print(json.dumps({**out, "state": state, "usage": read_usage()}, indent=2))
    elif cmd == "lane":
        if len(args) < 3:
            sys.exit("usage: otomode.py lane T<n> <lane> [--log FILE]")
        record_lane(args[1], args[2], lanes_log(dict(zip(args[3::2], args[4::2]))))
    elif cmd == "score":
        print(json.dumps(score(lanes_log(dict(zip(args[1::2], args[2::2])))), indent=2))
    elif cmd == "usage":
        print(json.dumps(read_usage(), indent=2))
    else:
        sys.exit(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
