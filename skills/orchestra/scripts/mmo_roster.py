"""Roster: which lanes really answer on this machine right now, and for which tier.

    python mmo_roster.py probe  [--out FILE] [--lanes a,b] [--models FILE] [-t SECONDS] [--max-age HOURS]
                                [--no-subagents] [--write] [--write-timeout SECONDS]
    python mmo_roster.py show   [--file FILE] [--max-age HOURS]
    python mmo_roster.py ready  --tier TIER [--for write] [--file FILE] [--max-age HOURS]
    python mmo_roster.py lineup [--file FILE] [--max-age HOURS]

`mmo-run --list` only says a CLI is installed. A probe sends one tiny read-only brief per lane and
model, once, so a lane that is out of credit, signed out or given a stale model id shows up before
any real work is routed to it. Tiers: strong, middle, cheap, bulk, opinion (no-tools lanes).
Exit codes: 0 ok, 2 usage, 3 roster missing or older than --max-age (probe again).

--write adds a second stage for every lane that answered and has tools (mmo_roster_write.py): one rw
brief in a throwaway git worktree, judged from the files it leaves, never from the lane's words.
can_write: a file appeared; can_run: both files hold what a real shell printed (true, false or
not-tested). `ready --for write` skips lanes whose can_run is false and `lineup` marks them "cannot run
commands". One call per lane, --write-timeout seconds (default 180), no retries.

Models file: lines `lane model` (`#` comments, blank lines ignored, several lines per lane are each
probed). Without --models, probe reads $MMO_MODELS, else ~/.config/mmo/models, when that file exists.
Tiers come from mmo_tiers.py, the one table shared with mmo-score.

A lane that failed with a limit and printed when it comes back (mmo-run puts retry_after=<UTC time> in
the out file header) is remembered: while that time is in the future, probe makes no call to that lane
and keeps its record, and show and lineup say "limit until <date time>". Once the time has passed the
lane is probed again as usual. A limit message with no recognisable time remembers nothing.
"""
import json
import io
import os
import re
import subprocess
import sys
import tempfile
import time

import mmo_limit
import mmo_roster_write
import mmo_tiers

HERE = os.path.dirname(os.path.abspath(__file__))
BASH = os.environ.get("MMO_BASH") or "bash"
BRIEF = "Reply with exactly the word PONG and nothing else."
TIERS = ("strong", "middle", "cheap", "bulk", "opinion")
DEFAULT_FILE = os.path.join(".mmo", "roster.json")

# Claude tiers run as the conductor's own sub-agents: listed, never probed (the conductor is one).
SUBAGENTS = [("opus", "strong"), ("sonnet", "middle"), ("haiku", "bulk")]

REASON = {  # three or four words for the lineup
    "auth": "not signed in", "model": "model id rejected", "needs-model": "needs a model id",
    "failed": "failed, see roster", "setup": "not configured",
}
FIX = {  # the wording of docs/failures.md: what to do
    "limit": "Route to another lane of the same tier; top up or wait for the reset. Waiting inside a run does not help",
    "auth": "Sign in once in a terminal (e.g. `<cli> login`). The runner never signs in for you",
    "model": "List the ids the CLI accepts and put one in the models file (`lane model`), then probe again",
    "needs-model": "This lane has no default model: add a line `<lane> <model id>` to the models file and probe again",
    "timeout": "Probe again with a longer -t; if it repeats, the CLI is waiting on a sign-in or an update",
    "failed": "Read the error line and run the lane once by hand with a one-line brief",
    "setup": "The CLI is installed but not configured; see docs/lanes/<lane>.md",
}
EXIT_STATUS = {0: "ok", 3: "failed", 4: "timeout", 5: "failed", 6: "limit", 7: "auth", 8: "model"}

SECRET = re.compile(
    r"(sk-[A-Za-z0-9_\-]{8,}|xox[a-z]-[A-Za-z0-9\-]+|gh[pousr]_[A-Za-z0-9]{16,}|AIza[0-9A-Za-z_\-]{20,}"
    r"|Bearer\s+\S+|(?i:(?:api[_-]?key|token|secret|password)\s*[=:]\s*)[^\s)\],;]+|[A-Za-z0-9_\-]{32,})")


def native(path):
    """Git Bash hands Windows Python /c/... paths; make them openable."""
    if os.name == "nt" and path and re.match(r"^/[a-zA-Z]/", path):
        return path[1].upper() + ":" + path[2:]
    return path


def mask(text):
    text = SECRET.sub("***", text)
    home = os.path.expanduser("~")
    for h in {home, home.replace("\\", "/")}:
        if len(h) > 3:
            text = text.replace(h, "~")
    text = re.sub(r"/[a-z]/Users/[^/\s]+", "~", text)
    return text[:200]


def tier_of(lane, model, ro):
    """Opinion for lanes without tools; else the shared table (mmo_tiers.py), then cheap."""
    if ro == "notools":
        return "opinion"
    tier = mmo_tiers.tier_of(lane, model)
    return "cheap" if tier == "unknown" else tier


def list_lanes(runner):
    out = subprocess.run([BASH, runner, "--list"], capture_output=True, text=True).stdout
    lanes = []
    for line in out.splitlines()[1:]:
        f = line.split()
        if len(f) >= 5:
            lanes.append({"lane": f[0], "cli": f[1], "family": f[2], "ro": f[3],
                          "default": f[5] if len(f) > 5 else ""})
    return lanes


def default_models_file():
    """The models file used when --models is not given: $MMO_MODELS, else ~/.config/mmo/models."""
    path = native(os.environ.get("MMO_MODELS") or "")
    if not path:
        home = native(os.environ.get("HOME") or "") or os.path.expanduser("~")  # HOME first: tests fake it
        path = os.path.join(home, ".config", "mmo", "models")
    return path if os.path.isfile(path) else ""


def read_models(path):
    models = {}
    if not path:
        return models
    with open(native(path), encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].split()
            if len(line) >= 2:
                models.setdefault(line[0], []).append(line[1])
    return models


def error_line(out_file):
    """The one line that says why, from the lane's out file (never the brief)."""
    try:
        with open(out_file, encoding="utf-8", errors="replace") as f:
            lines = [ln.strip() for ln in f.read().splitlines()[1:]]
    except OSError:
        return ""
    lines = [ln for ln in lines if ln and BRIEF not in ln and not ln.startswith("LANE DID NOT PRODUCE")
             and not ln.startswith("READ-ONLY LANE")]
    pick = ""
    for ln in lines:
        if re.search(r"error|limit|quota|denied|auth|sign|log ?in|model|balance|subscription|\b4\d\d\b", ln, re.I):
            pick = ln
    return mask(pick or (lines[-1] if lines else ""))


def header_value(out_file, key):
    """A key=value field of the out file's header line, or ''."""
    try:
        with open(out_file, encoding="utf-8", errors="replace") as f:
            m = re.search(r"%s=(\S+)" % re.escape(key), f.readline())
    except OSError:
        return ""
    return m.group(1) if m else ""


def held_until(prev, lane, model):
    """(retry_after, error) of an earlier limit record whose return time is still ahead, else None."""
    for r in (prev or {}).get("lanes", []):
        if r.get("lane") == lane and r.get("model") == model and r.get("status") == "limit":
            when = mmo_limit.future(r.get("retry_after"))
            if when:
                return r["retry_after"], r.get("error", "")
    return None


def probe(opts):
    out = native(opts.get("--out") or DEFAULT_FILE)
    max_age = opts.get("--max-age")
    if max_age is not None:
        old = load(out)
        if old and age_hours(old) <= float(max_age):
            print_table(old)
            return 0
    runner = os.environ.get("MMO_RUN") or os.path.join(HERE, "mmo-run")
    timeout = int(opts.get("-t") or 90)
    models = read_models(opts.get("--models") or default_models_file())
    want = [x for x in (opts.get("--lanes") or "").split(",") if x]
    known = list_lanes(runner)
    if want:
        names = {lane["lane"] for lane in known}
        missing = [w for w in want if w not in names]
        if missing:
            raise SystemExit("mmo-roster: unknown lane(s): " + ", ".join(missing))
        known = [lane for lane in known if lane["lane"] in want]
    else:
        # The conductor's own model family is reached through sub-agents, not print mode.
        known = [lane for lane in known if lane["cli"] in ("ok", "setup") and lane["lane"] != "claude"]

    now = time.time()
    prev = load(out)
    results, jobs = [], []
    for lane in known:
        base = {"lane": lane["lane"], "family": lane["family"], "ro": lane["ro"], "kind": "external",
                "checked": now, "seconds": 0, "error": ""}
        if lane["cli"] != "ok":
            results.append(dict(base, model=lane["default"], status="setup" if lane["cli"] == "setup" else "absent"))
            continue
        ids = models.get(lane["lane"]) or ([lane["default"]] if lane["default"] else [])
        if not ids:
            results.append(dict(base, model="", status="needs-model"))
            continue
        for m in ids:
            held = held_until(prev, lane["lane"], m)
            if held:  # still limited by its own account of when it returns: no call, keep the record
                results.append(dict(base, model=m, status="limit", error=held[1], retry_after=held[0], seconds=0))
            else:
                jobs.append(dict(base, model=m))

    tmp = tempfile.mkdtemp(prefix="mmo-roster-")
    brief = os.path.join(tmp, "brief.md")
    with open(brief, "w", encoding="utf-8") as f:
        f.write(BRIEF + "\n")
    work = os.path.join(tmp, "work")  # not a git repo: throwaway lanes need no worktree
    os.makedirs(work)
    env = dict(os.environ)
    env.pop("MMO_LOG", None)  # probes are not tasks; keep them out of the scoreboard
    fwd = lambda p: p.replace("\\", "/")
    for start in range(0, len(jobs), 4):
        batch = []
        for i, job in enumerate(jobs[start:start + 4]):
            if i:
                time.sleep(1)  # two lanes on one CLI started in the same second collide on its storage
            job["_out"] = os.path.join(tmp, "%d.md" % (start + i))
            cmd = [BASH, runner, job["lane"], "--mode", "ro", "-C", fwd(work), "-t", str(timeout),
                   "--brief", fwd(brief), "--out", fwd(job["_out"])]
            if job["model"]:
                cmd[3:3] = ["-m", job["model"]]
            job["_t0"] = time.time()
            job["_p"] = subprocess.Popen(cmd, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            batch.append(job)
        for job in batch:
            try:
                code = job["_p"].wait(timeout=timeout + 30)
            except subprocess.TimeoutExpired:
                job["_p"].kill()
                code = 4
            job["seconds"] = int(time.time() - job["_t0"])
            job["status"] = EXIT_STATUS.get(code, "failed")
            if job["status"] not in ("ok", "timeout"):  # a timeout has no error line worth keeping
                job["error"] = error_line(job["_out"])
            if job["status"] == "limit":
                job["retry_after"] = header_value(job["_out"], "retry_after")
                if not job["retry_after"]:
                    del job["retry_after"]
            for k in ("_out", "_t0", "_p"):
                job.pop(k)
            results.append(job)

    if opts.get("--write"):
        wjobs = [r for r in results if r["status"] == "ok" and r["ro"] != "notools"]
        mmo_roster_write.write_probe(wjobs, runner, BASH, env, int(opts.get("--write-timeout") or 180))

    if not opts.get("--no-subagents"):
        results += [{"lane": "subagent", "model": m, "family": "anthropic", "ro": "sandbox", "kind": "subagent",
                     "status": "ok", "checked": now, "seconds": 0, "error": ""} for m, _ in SUBAGENTS]
    for r in results:
        r["tier"] = dict(SUBAGENTS).get(r["model"]) if r["kind"] == "subagent" else tier_of(r["lane"], r["model"], r["ro"])
        note = mmo_tiers.note_of(r["lane"])
        if note:
            r["note"] = note
        r.setdefault("can_write", "not-tested")
        r.setdefault("can_run", "not-tested")
        r["ready"] = r["status"] == "ok"
        if not r["ready"] and r["status"] in FIX:
            r["fix"] = FIX[r["status"]]

    old = load(out) if want else None
    if old:  # a partial probe updates its lanes and keeps the rest
        fresh_sub = any(r["kind"] == "subagent" for r in results)
        keep = [r for r in old["lanes"] if r["lane"] not in want and not (fresh_sub and r["kind"] == "subagent")]
        results = keep + results
    roster = {"version": 1, "lanes": results}
    add_pass_rates(roster)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(roster, f, indent=1)
    print_table(roster)
    return 0


def add_pass_rates(roster):
    """First-try pass rate per lane from $MMO_LOG, only with 5 or more checked tasks."""
    log = native(os.environ.get("MMO_LOG") or "")
    if not log or not os.path.isfile(log):
        return
    last, seen, tally = {}, {}, {}
    with open(log, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            task = ev.get("task") or ""
            if not task:
                continue
            if ev.get("kind") == "run":
                last[task] = "%s %s" % (ev.get("provider"), ev.get("model"))
            elif ev.get("kind") == "lane":  # otomode records Claude sub-agent launches this way
                last[task] = "subagent %s" % ev.get("lane")
            elif ev.get("kind") == "check" and task in last and task not in seen:
                seen[task] = 1
                c = tally.setdefault(last[task], [0, 0])
                c[1] += 1
                c[0] += ev.get("status") == "pass"
    for r in roster["lanes"]:
        c = tally.get("%s %s" % (r["lane"], r["model"]))
        if c and c[1] >= 5:
            r["pass"] = "%d/%d" % tuple(c)


def load(path):
    try:
        with open(native(path), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def age_hours(roster):
    probed = [r["checked"] for r in roster["lanes"] if r["kind"] == "external"] or \
             [r["checked"] for r in roster["lanes"]] or [0]
    return (time.time() - min(probed)) / 3600.0


def ranked(roster, tier, for_write=False):
    """Ready lanes of a tier, best first: the preference file, then external before sub-agents
    (the other way round for the strong tier), then the measured pass rate."""
    def rate(r):
        if "pass" not in r:
            return -1.0
        a, b = r["pass"].split("/")
        return int(a) / float(b)
    rows = [r for r in roster["lanes"] if r["ready"] and r["tier"] == tier
            and not (for_write and r.get("can_run") == "false")]
    # The strong tier is the exception to "external first": the hardest work goes to the Claude
    # sub-agent (Opus) when it is ready, and the external strong lanes are its fallback.
    sub_last = tier != "strong"
    rows = sorted(rows, key=lambda r: ((r["kind"] == "subagent") == sub_last, -rate(r)))
    # A preference file overrides both rules: lines "tier lane [model]", in the order wanted.
    wanted = [w for w in read_prefer() if w[0] == tier]
    def pref(r):
        for i, w in enumerate(wanted):
            if w[1] == r["lane"] and (len(w) < 3 or w[2] == (r.get("model") or "")):
                return i
        return len(wanted)
    return sorted(rows, key=pref)


def read_prefer():
    """Lines of the preference file ($MMO_PREFER or ~/.config/mmo/prefer); missing file means none."""
    path = os.environ.get("MMO_PREFER") or os.path.join(
        os.environ.get("HOME") or os.path.expanduser("~"), ".config", "mmo", "prefer")
    out = []
    try:
        with io.open(path, encoding="utf-8") as f:
            for line in f:
                parts = line.split("#", 1)[0].split()
                if len(parts) >= 2:
                    out.append(parts[:3])
    except (IOError, OSError):
        pass
    return out


def name(r):
    return ("Claude %s (sub-agent)" % r["model"]) if r["kind"] == "subagent" else "%s %s" % (r["lane"], r["model"] or "-")


def write_cell(r):
    w, x = r.get("can_write", "not-tested"), r.get("can_run", "not-tested")
    if r["kind"] == "subagent" or (w == "not-tested" and x == "not-tested"):
        return "-"
    return "ok" if x == "true" else ("no-run" if w == "true" else "no-write")


def labelled(r):
    note = " (cannot run commands: give it answer-only work)" if r.get("can_run") == "false" else ""
    return name(r) + note


def reason(r):
    if r["status"] == "limit":
        e = r.get("error", "")
        when = mmo_limit.local_text(r.get("retry_after"))
        if when:
            return "limit until %s" % when
        if re.search(r"subscription|plan", e, re.I):
            return "plan lapsed"
        m = re.search(r"(?:try again (?:at|after|in)|resets? (?:at|on|in))\s+([^.;)]{3,24})", e, re.I) or \
            re.search(r"(\d{4}-\d\d-\d\d)", e)
        return "limit until %s" % m.group(1).strip() if m else "usage limit reached"
    if r["status"] == "timeout":
        return "no answer in %ss" % r["seconds"]
    return REASON.get(r["status"], r["status"])


def print_table(roster):
    h = age_hours(roster)
    print("roster: %d lanes, probed %.1f h ago" % (len(roster["lanes"]), h))
    print("%-16s %-30s %-8s %-11s %-6s %-6s %-9s %s" % ("LANE", "MODEL", "TIER", "STATUS", "SECS", "PASS", "WRITE", "WHY / FIX"))
    for r in sorted(roster["lanes"], key=lambda r: (not r["ready"], TIERS.index(r["tier"]), r["kind"] == "subagent")):
        said = reason(r) if r.get("retry_after") and r["status"] == "limit" else (r.get("error") or reason(r))
        why = "" if r["ready"] else "%s. %s" % (said.rstrip("."), r.get("fix", ""))
        print("%-16s %-30s %-8s %-11s %-6s %-6s %-9s %s" % (r["lane"], r["model"] or "-", r["tier"],
              "READY" if r["ready"] else r["status"], r["seconds"], r.get("pass", "-"), write_cell(r), why.strip(". ")))


def lineup(roster):
    """A short block to tell the user which models will play which part."""
    lines = ["Lineup (roster %.1f h old):" % age_hours(roster)]
    for tier, label in (("strong", "strong"), ("middle", "middle"), ("cheap", "cheap"), ("bulk", "bulk")):
        rows = ranked(roster, tier)
        if rows:
            extra = " (then %s)" % labelled(rows[1]) if len(rows) > 1 else ""
            lines.append("  %s: %s%s" % (label, labelled(rows[0]), extra))
        else:
            lines.append("  %s: nothing ready" % label)
    # Second opinion: another family than the conductor's, a strong or middle lane first.
    other = [r for t in ("strong", "middle", "opinion", "cheap") for r in ranked(roster, t) if r["family"] != "anthropic"]
    lines.append("  second opinion: %s" % (labelled(other[0]) if other else "nothing ready outside Claude"))
    down = [r for r in roster["lanes"] if not r["ready"] and r["status"] != "absent"]
    if down:
        lines.append("  not usable now: " + ", ".join("%s (%s)" % (r["lane"], reason(r)) for r in down))
    return "\n".join(lines)


def parse(argv):
    opts, i = {}, 0
    flags = ("--no-subagents", "--write")
    while i < len(argv):
        a = argv[i]
        if a in flags:
            opts[a] = True
            i += 1
        elif a.startswith("-") and i + 1 < len(argv):
            opts[a] = argv[i + 1]
            i += 2
        else:
            raise SystemExit("mmo-roster: bad argument %s\n%s" % (a, __doc__))
    return opts


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("probe", "show", "ready", "lineup"):
        sys.stderr.write(__doc__)
        return 2
    cmd, opts = sys.argv[1], parse(sys.argv[2:])
    if cmd == "probe":
        return probe(opts)
    path = opts.get("--file") or DEFAULT_FILE
    roster = load(path)
    if roster is None:
        sys.stderr.write("mmo-roster: no roster at %s; run `mmo-roster probe`\n" % path)
        return 3
    stale = age_hours(roster) > float(opts.get("--max-age") or 12)
    if cmd == "show":
        print_table(roster)
    elif cmd == "lineup":
        print(lineup(roster))
    else:
        tier = opts.get("--tier")
        if tier not in TIERS:
            sys.stderr.write("mmo-roster: --tier is one of %s\n" % ", ".join(TIERS))
            return 2
        if opts.get("--for") not in (None, "write"):
            sys.stderr.write("mmo-roster: --for takes only `write`\n")
            return 2
        for r in ranked(roster, tier, opts.get("--for") == "write"):
            print("%s %s" % (r["lane"], r["model"] or "-"))
    if stale:
        sys.stderr.write("mmo-roster: roster is older than %s h; probe again\n" % (opts.get("--max-age") or 12))
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
