"""Claude Code PreToolUse hook: a sub-agent call must name its model.

A sub-agent started without a model inherits the main model. In the repo's A/B test, naming a cheaper
model on every call cut the cost per run from $3.21 to about $1.49 (see docs/cost.md).

  python mmo_model_guard.py hook                      (what Claude Code runs; event JSON on stdin)
  python mmo_model_guard.py install [--settings FILE]   register it (default ~/.claude/settings.json)
  python mmo_model_guard.py uninstall [--settings FILE]

MMO_MODEL_GUARD=warn  lets the call through with a warning instead of denying it.
MMO_MODEL_GUARD=off   disables the guard.
A fork (tool_input.subagent_type == "fork") inherits the parent by design and is always allowed.
"""
import json
import os
import sys

AGENT_TOOLS = ("Agent", "Task")   # "Task" in older Claude Code versions
MATCHER = "Agent|Task"
MARK = "mmo_model_guard.py"       # how install/uninstall recognise their own entry
REASON = ("Name a model on every sub-agent call (model: sonnet, opus or haiku). A call without one "
          "inherits the expensive main model, which measured about twice the cost for the same result.")


def decide(event, mode):
    """Return (decision, message): decision is "deny", "warn" or None."""
    if mode == "off":
        return None, ""
    if event.get("tool_name") not in AGENT_TOOLS:
        return None, ""
    tool_input = event.get("tool_input") or {}
    if str(tool_input.get("subagent_type") or "").strip().lower() == "fork":
        return None, ""
    model = tool_input.get("model")
    if isinstance(model, str) and model.strip():
        return None, ""
    return ("warn" if mode == "warn" else "deny"), REASON


def hook():
    try:
        event = json.loads(sys.stdin.buffer.read().decode("utf-8-sig", errors="replace") or "{}")
    except ValueError:
        return
    if not isinstance(event, dict):
        return
    mode = os.environ.get("MMO_MODEL_GUARD", "").strip().lower()
    decision, message = decide(event, mode)
    if decision == "deny":
        out = {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                      "permissionDecision": "deny",
                                      "permissionDecisionReason": message}}
    elif decision == "warn":
        # No permissionDecision: the call goes on through the normal permission flow, the agent sees the note.
        out = {"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                      "additionalContext": "mmo_model_guard (warn mode): " + message}}
        sys.stderr.write("mmo_model_guard: " + message + "\n")
    else:
        return
    sys.stdout.write(json.dumps(out))


def hook_command():
    script = os.path.abspath(__file__).replace("\\", "/")
    exe = sys.executable.replace("\\", "/")
    return '"%s" "%s" hook' % (exe, script)


def default_settings():
    return os.path.join(os.path.expanduser("~"), ".claude", "settings.json")


def install(path, remove=False):
    """Merge our PreToolUse entry into settings.json; never touch anyone else's entries."""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    if not isinstance(data, dict):
        sys.exit("settings file is not a JSON object: " + path)
    if remove and not os.path.exists(path):
        print("nothing to remove: " + path + " does not exist")
        return
    hooks = data.setdefault("hooks", {})
    entries = hooks.get("PreToolUse", [])
    kept = []
    for e in entries:
        mine = [h for h in e.get("hooks", []) if MARK in h.get("command", "")]
        if not mine:
            kept.append(e)
            continue
        rest = [h for h in e.get("hooks", []) if MARK not in h.get("command", "")]
        if rest:   # an entry we share with another hook: keep the other hook only
            kept.append(dict(e, hooks=rest))
    if not remove:
        kept.append({"matcher": MATCHER,
                     "hooks": [{"type": "command", "command": hook_command(), "timeout": 10}]})
    if kept:
        hooks["PreToolUse"] = kept
    else:
        hooks.pop("PreToolUse", None)
    if not hooks:
        data.pop("hooks", None)
    if os.path.exists(path):
        os.replace(path, path + ".bak")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(("removed from " if remove else "installed in ") + path)


def main(argv):
    cmd = argv[0] if argv else ""
    if cmd == "hook":
        hook()
    elif cmd in ("install", "uninstall"):
        path = default_settings()
        if "--settings" in argv:
            k = argv.index("--settings")
            if k + 1 >= len(argv):
                sys.exit("--settings needs a file")
            path = argv[k + 1]
        install(path, remove=cmd == "uninstall")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
