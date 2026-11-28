"""mmo_cloud.py: the logic behind mmo-cloud. Stdlib only.

Each agent is written from vendor documentation only (see docs/lanes/cloud.md) and has never
been run against a real account. Response fields that the docs did not pin down are read
defensively, and anything unknown is reported, never guessed into a success.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

CHECKED = "docs-2026-11-28"
EXIT = {"ok": 0, "usage": 2, "failed": 3, "timeout": 4, "empty": 5, "limit": 6, "auth": 7,
        "waiting": 10}
# Exit code per normalized state. queued and running are not failures: status reports them with 0.
STATE_EXIT = {"queued": 0, "running": 0, "done": 0, "failed": 3, "cancelled": 3, "expired": 3,
              "limit": 6, "auth": 7, "waiting": 10}
TERMINAL = {"done", "failed", "cancelled", "expired", "limit", "auth", "waiting"}

AGENTS = {
    "devin": {"keys": ["DEVIN_API_KEY", "DEVIN_ORG_ID"], "base_env": "MMO_DEVIN_BASE",
              "base": "https://api.devin.ai", "cap": "acu", "cancel": True,
              "note": "Devin v3 REST, service-user key (cog_...)"},
    "cursor": {"keys": ["CURSOR_API_KEY"], "base_env": "MMO_CURSOR_BASE",
               "base": "https://api.cursor.com", "cap": None, "cancel": True,
               "note": "Cursor cloud agents API v1 (public beta)",
               "nocap": "Cursor documents no cost or time cap for a cloud agent run"},
    "copilot": {"keys": ["COPILOT_AGENT_TOKEN"], "base_env": "MMO_COPILOT_BASE",
                "base": "https://api.github.com", "cap": None, "cancel": False,
                "note": "GitHub agent tasks REST (public preview), fine-grained PAT",
                "nocap": "GitHub documents no cost cap; the vendor stops a session at 59 minutes"},
}
LEFT_OUT = ("jules (session states and cancel undocumented), codex-cloud (exec/status output "
            "undocumented, returns a diff not a branch), claude-cloud (no status endpoint)")

DEVIN_LIMIT = {"usage_limit_exceeded", "out_of_credits", "out_of_quota", "no_quota_allocation",
               "payment_declined", "org_usage_limit_exceeded", "user_usage_limit_exceeded",
               "total_session_limit_exceeded", "contract_expired"}


class Stop(Exception):
    """A clean stop with a normalized state, an exit code and a one-line reason."""

    def __init__(self, state, code, msg):
        super().__init__(msg)
        self.state, self.code, self.msg = state, code, msg


def usage(msg):
    raise Stop("usage", 2, msg)


def secrets(agent):
    return [os.environ.get(k, "") for k in AGENTS[agent]["keys"] if os.environ.get(k)]


def scrub(agent, text):
    # A vendor could echo a header back in an error body. Never let a key reach output.
    text = str(text)
    for s in secrets(agent):
        if len(s) >= 4:
            text = text.replace(s, "***")
    return text


def header(agent, status, **kw):
    parts = ["agent=" + agent, "status=" + status]
    parts += ["%s=%s" % (k, str(v).replace(" ", "_")) for k, v in kw.items() if v not in (None, "")]
    print("<!-- mmo-cloud %s -->" % " ".join(parts))


def need_keys(agent):
    missing = [k for k in AGENTS[agent]["keys"] if not os.environ.get(k)]
    if missing:
        raise Stop("auth", 7, "%s is not set (keys come from the environment only)" % ", ".join(missing))


def base(agent):
    return os.environ.get(AGENTS[agent]["base_env"], AGENTS[agent]["base"]).rstrip("/")


def auth_headers(agent):
    if agent == "devin":
        return {"Authorization": "Bearer " + os.environ["DEVIN_API_KEY"]}
    if agent == "cursor":
        return {"Authorization": "Bearer " + os.environ["CURSOR_API_KEY"]}
    return {"Authorization": "Bearer " + os.environ["COPILOT_AGENT_TOKEN"],
            "X-GitHub-Api-Version": "2026-03-10", "Accept": "application/vnd.github+json"}


def http(agent, method, path, body=None, timeout=30):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base(agent) + path, data=data, method=method)
    for k, v in auth_headers(agent).items():
        req.add_header(k, v)
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            code, raw = r.status, r.read()
    except urllib.error.HTTPError as e:
        code, raw = e.code, e.read()
    except (urllib.error.URLError, OSError) as e:
        raise Stop("failed", 3, "cannot reach %s: %s" % (agent, scrub(agent, getattr(e, "reason", e))))
    try:
        js = json.loads(raw.decode("utf-8", "replace")) if raw else {}
    except ValueError:
        js = {"_text": raw.decode("utf-8", "replace")[:300]}
    if code >= 400:
        state = classify_http(agent, code, js)
        raise Stop(state, STATE_EXIT[state], "HTTP %d from %s: %s" % (code, agent, scrub(agent, short(js))))
    return js


def short(js):
    if isinstance(js, dict):
        err = js.get("error")
        if isinstance(err, dict):
            return "%s %s" % (err.get("code", ""), err.get("message", ""))
        for k in ("detail", "message", "_text"):
            if js.get(k):
                return str(js[k])[:300]
    return str(js)[:300]


def classify_http(agent, code, js):
    err = js.get("error") if isinstance(js, dict) else None
    ecode = err.get("code", "") if isinstance(err, dict) else ""
    if code in (402, 429) or ecode in ("plan_required", "rate_limit_exceeded"):
        return "limit"
    if code in (401, 403):
        return "auth"
    return "failed"


def first(d, *keys):
    for k in keys:
        if isinstance(d, dict) and d.get(k):
            return d[k]
    return ""


# ---------------------------------------------------------------- vendor mappings

def map_devin(s):
    st, det = s.get("status", ""), s.get("status_detail", "") or ""
    if det in DEVIN_LIMIT:
        return "limit"
    if det in ("waiting_for_user", "waiting_for_approval"):
        return "waiting"
    if det == "user_request":
        return "cancelled"
    if det == "inactivity":
        return "expired"
    if det == "error" or st == "error":
        return "failed"
    if det == "finished":
        return "done"
    if det == "working":
        return "running"
    return {"new": "queued", "claimed": "queued", "running": "running", "resuming": "running",
            "exit": "done", "suspended": "waiting"}.get(st, "unknown")


CURSOR_RUN = {"CREATING": "queued", "RUNNING": "running", "WAITING_FOR_BACKGROUND_WORK": "running",
              "FINISHED": "done", "ERROR": "failed", "CANCELLED": "cancelled", "EXPIRED": "expired"}

COPILOT = {"queued": "queued", "in_progress": "running", "completed": "done", "failed": "failed",
           "waiting_for_user": "waiting", "timed_out": "expired", "cancelled": "cancelled"}


def map_copilot(t):
    st = t.get("state", "")
    if st == "idle":
        # idle is not explained in the docs: with a pull or branch artifact the work is there to
        # check; without one the agent stopped and needs a person.
        return "done" if t.get("artifacts") else "waiting"
    return COPILOT.get(st, "unknown")


# ---------------------------------------------------------------- start

def prompt_for(brief, repo, basebr):
    tail = "\n\nRepository: %s." % repo
    if basebr:
        tail += " Start from branch %s." % basebr
    return brief + tail + " Put your work on a new branch and open a pull request. Do not merge it."


def start(agent, brief, repo, basebr, cap):
    if agent == "devin":
        org = os.environ["DEVIN_ORG_ID"]
        body = {"prompt": prompt_for(brief, repo, basebr), "max_acu_limit": cap,
                "title": "mmo-cloud: " + repo}
        js = http(agent, "POST", "/v3/organizations/%s/sessions" % org, body)
        sid = first(js, "session_id", "devin_id", "id")
        return {"id": sid, "url": first(js, "url")}
    if agent == "cursor":
        repo0 = {"url": "https://github.com/" + repo}
        if basebr:
            repo0["startingRef"] = basebr
        js = http(agent, "POST", "/v1/agents",
                  {"prompt": {"text": prompt_for(brief, repo, basebr)}, "repos": [repo0],
                   "autoCreatePR": True})
        ag = js.get("agent", js) if isinstance(js.get("agent"), dict) else js
        run = js.get("run") if isinstance(js.get("run"), dict) else {}
        return {"id": first(ag, "id"), "run_id": first(run, "id") or first(ag, "latestRunId"),
                "url": first(ag, "url")}
    owner, name = repo.split("/", 1)
    body = {"prompt": prompt_for(brief, repo, basebr), "create_pull_request": True}
    if basebr:
        body["base_ref"] = basebr
    js = http(agent, "POST", "/agents/repos/%s/%s/tasks" % (owner, name), body)
    return {"id": str(first(js, "id")), "url": first(js, "html_url", "url")}


# ---------------------------------------------------------------- status / result / cancel

def fetch(st):
    agent, sid = st["agent"], st["id"]
    if agent == "devin":
        js = http(agent, "GET", "/v3/organizations/%s/sessions/%s" % (os.environ["DEVIN_ORG_ID"], sid))
        return map_devin(js), "%s/%s" % (js.get("status", ""), js.get("status_detail", "") or "-"), js
    if agent == "cursor":
        run_id = st.get("run_id")
        ag = None
        if not run_id:
            ag = http(agent, "GET", "/v1/agents/%s" % sid)
            run_id = ag.get("latestRunId", "")
            st["run_id"] = run_id
        if not run_id:
            return "queued", "no-run", ag
        run = http(agent, "GET", "/v1/agents/%s/runs/%s" % (sid, run_id))
        if not run.get("git"):
            # The docs show git.branches without saying whether it sits on the run or the agent.
            ag = ag if ag is not None else http(agent, "GET", "/v1/agents/%s" % sid)
            if ag.get("git"):
                run["git"] = ag["git"]
        return CURSOR_RUN.get(run.get("status", ""), "unknown"), run.get("status", ""), run
    owner, name = st["repo"].split("/", 1)
    js = http(agent, "GET", "/agents/repos/%s/%s/tasks/%s" % (owner, name, sid))
    return map_copilot(js), js.get("state", ""), js


def outputs(agent, js, repo):
    prs, branches = [], []
    if agent == "devin":
        for p in js.get("pull_requests") or []:
            if isinstance(p, dict) and p.get("pr_url"):
                prs.append(p["pr_url"])
    elif agent == "cursor":
        for b in (js.get("git") or {}).get("branches") or []:
            if isinstance(b, dict):
                if b.get("prUrl"):
                    prs.append(b["prUrl"])
                if b.get("branch"):
                    branches.append(b["branch"])
    else:
        for a in js.get("artifacts") or []:
            if not isinstance(a, dict):
                continue
            data = a.get("data") or {}
            if a.get("type") == "pull" and data.get("id") is not None:
                prs.append("%s pull id %s" % (repo, data["id"]))
            if a.get("type") == "branch" and data.get("head_ref"):
                branches.append(data["head_ref"])
    return prs, branches


def load_state(path):
    try:
        with open(path, encoding="utf-8") as f:
            st = json.load(f)
    except (OSError, ValueError) as e:
        usage("cannot read state file %s: %s" % (path, e))
    if st.get("agent") not in AGENTS or not st.get("id"):
        usage("state file %s is not an mmo-cloud state" % path)
    return st


def save_state(path, st):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(st, f, indent=1)
    try:
        os.chmod(tmp, 0o600)
    except OSError:
        pass
    os.replace(tmp, path)


def status_once(path, st):
    need_keys(st["agent"])
    state, vendor, js = fetch(st)
    note = ""
    if state == "unknown":
        # A state the docs did not list is not trusted as progress or success.
        state, note = "failed", "unknown_vendor_state"
    st["last_status"], st["last_vendor"] = state, vendor
    st["checked"] = now()
    save_state(path, st)
    return state, vendor, note, js


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------- commands

def parse(argv, spec):
    out, i = {}, 0
    while i < len(argv):
        a = argv[i]
        if a not in spec:
            usage("unknown option: %s" % a)
        if i + 1 >= len(argv):
            usage("%s needs a value" % a)
        out[spec[a]] = argv[i + 1]
        i += 2
    return out


def cmd_list(_argv):
    print("%-9s %-6s %-12s %-7s %-16s %s" % ("AGENT", "KEY", "CAP", "CANCEL", "CHECKED", "NEEDS"))
    for a, d in AGENTS.items():
        have = "ok" if all(os.environ.get(k) for k in d["keys"]) else "absent"
        cap = "acu (--cap)" if d["cap"] else "none"
        print("%-9s %-6s %-12s %-7s %-16s %s" % (a, have, cap, "yes" if d["cancel"] else "no",
                                                CHECKED, " ".join(d["keys"])))
    print("not supported: " + LEFT_OUT)
    return 0


def cmd_start(argv):
    if not argv:
        usage("start <agent> --brief FILE --repo OWNER/NAME [--base BRANCH] [--cap N] --state FILE")
    agent = argv[0]
    if agent not in AGENTS:
        usage("unknown agent: %s (known: %s)" % (agent, ", ".join(AGENTS)))
    o = parse(argv[1:], {"--brief": "brief", "--repo": "repo", "--base": "base", "--cap": "cap",
                         "--state": "state"})
    for k in ("brief", "repo", "state"):
        if not o.get(k):
            usage("--%s is required" % k)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", o["repo"]):
        usage("--repo must be OWNER/NAME")
    if o.get("base") and not re.fullmatch(r"[A-Za-z0-9_./-]+", o["base"]):
        usage("--base is not a branch name")
    try:
        with open(o["brief"], encoding="utf-8") as f:
            brief = f.read()
    except OSError as e:
        usage("cannot read brief: %s" % e)
    if not brief.strip():
        usage("--brief must name a non-empty file")
    d, cap = AGENTS[agent], None
    if d["cap"]:
        if not o.get("cap"):
            usage("%s supports a cost cap: pass --cap N (%s units) so a run cannot spend without limit"
                  % (agent, d["cap"].upper()))
        if not re.fullmatch(r"[1-9][0-9]*", o["cap"]):
            usage("--cap must be a positive whole number")
        cap = int(o["cap"])
    elif o.get("cap"):
        usage("%s has no cap to pass --cap to: %s" % (agent, d["nocap"]))
    need_keys(agent)
    if os.path.exists(o["state"]):
        usage("state file %s exists: one state file per run" % o["state"])
    r = start(agent, brief, o["repo"], o.get("base", ""), cap)
    if not r.get("id"):
        raise Stop("failed", 3, "%s accepted the request but returned no session id" % agent)
    st = {"agent": agent, "id": r["id"], "url": r.get("url", ""), "repo": o["repo"],
          "base": o.get("base", ""), "started": now(), "started_epoch": int(time.time()),
          "cap": "%d %s" % (cap, d["cap"]) if cap else "none", "checked_against": CHECKED}
    if r.get("run_id"):
        st["run_id"] = r["run_id"]
    save_state(o["state"], st)
    header(agent, "started", id=r["id"], cap=("%d%s" % (cap, d["cap"])) if cap else "none",
           url=r.get("url"))
    if not cap:
        print("note: %s" % d["nocap"])
    return 0


def cmd_status(argv):
    o = parse(argv, {"--state": "state"})
    if not o.get("state"):
        usage("status --state FILE")
    st = load_state(o["state"])
    try:
        state, vendor, note, _ = status_once(o["state"], st)
    except Stop as s:
        header(st["agent"], s.state, id=st["id"])
        raise
    header(st["agent"], state, id=st["id"], vendor=vendor, note=note)
    return STATE_EXIT[state]


def cmd_wait(argv):
    o = parse(argv, {"--state": "state", "-t": "t", "--every": "every"})
    if not o.get("state") or not o.get("t"):
        usage("wait --state FILE -t SECONDS [--every SECONDS]")
    try:
        limit, every = float(o["t"]), float(o.get("every", "60"))
    except ValueError:
        usage("-t and --every take seconds")
    if limit <= 0 or every <= 0:
        usage("-t and --every must be positive")
    st = load_state(o["state"])
    deadline = time.monotonic() + limit
    while True:
        try:
            state, vendor, note, _ = status_once(o["state"], st)
        except Stop as s:
            header(st["agent"], s.state, id=st["id"])
            raise
        if state in TERMINAL:
            header(st["agent"], state, id=st["id"], vendor=vendor, note=note)
            return STATE_EXIT[state]
        left = deadline - time.monotonic()
        if left <= 0:
            # Timing out does not cancel the remote run; the conductor decides that.
            header(st["agent"], "timeout", id=st["id"], vendor=vendor)
            return EXIT["timeout"]
        time.sleep(min(every, left))


def cmd_result(argv):
    o = parse(argv, {"--state": "state"})
    if not o.get("state"):
        usage("result --state FILE")
    st = load_state(o["state"])
    need_keys(st["agent"])
    try:
        state, vendor, note, js = status_once(o["state"], st)
    except Stop as s:
        header(st["agent"], s.state, id=st["id"])
        raise
    prs, branches = outputs(st["agent"], js, st["repo"])
    header(st["agent"], state, id=st["id"], vendor=vendor, note=note)
    for p in prs:
        print("pr=" + p)
    for b in branches:
        print("branch=" + b)
    if not prs and not branches:
        print("no pull request or branch reported yet")
        return EXIT["empty"]
    if state != "done":
        print("note: the run is %s; the branch may still change" % state)
    print("note: this is a claim. Fetch the branch into a worktree, run the check, read the diff.")
    return 0


def cmd_cancel(argv):
    o = parse(argv, {"--state": "state"})
    if not o.get("state"):
        usage("cancel --state FILE")
    st = load_state(o["state"])
    agent = st["agent"]
    if not AGENTS[agent]["cancel"]:
        usage("no documented cancel for %s: stop it from the vendor's page" % agent)
    need_keys(agent)
    if agent == "devin":
        http(agent, "DELETE", "/v3/organizations/%s/sessions/%s" % (os.environ["DEVIN_ORG_ID"], st["id"]))
    else:
        run_id = st.get("run_id") or http(agent, "GET", "/v1/agents/%s" % st["id"]).get("latestRunId")
        if not run_id:
            raise Stop("failed", 3, "cursor agent %s has no run to cancel" % st["id"])
        http(agent, "POST", "/v1/agents/%s/runs/%s/cancel" % (st["id"], run_id), {})
    st["last_status"], st["checked"] = "cancelled", now()
    save_state(o["state"], st)
    header(agent, "cancelled", id=st["id"])
    return 0


COMMANDS = {"list": cmd_list, "start": cmd_start, "status": cmd_status, "wait": cmd_wait,
            "result": cmd_result, "cancel": cmd_cancel}


def main(argv):
    if not argv or argv[0] not in COMMANDS:
        print("mmo-cloud: usage: mmo-cloud list|start|status|wait|result|cancel ...", file=sys.stderr)
        return 2
    try:
        return COMMANDS[argv[0]](argv[1:])
    except Stop as s:
        agent = argv[1] if argv[0] == "start" and len(argv) > 1 and argv[1] in AGENTS else None
        if argv[0] == "start" and agent and s.state != "usage":
            header(agent, s.state)
        msg = scrub(agent, s.msg) if agent else s.msg
        for a in AGENTS:
            msg = scrub(a, msg)
        print("mmo-cloud: " + msg, file=sys.stderr)
        return s.code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
