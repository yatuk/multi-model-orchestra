"""Per-lane scoreboard from the lines mmo-run and mmo-check append to $MMO_LOG.

    python mmo_score.py [FILE] [--share | --routes | --councils | --task ID | --cost [--prices FILE]]
    python mmo_score.py --reports DIR [--lines N]
    python mmo_score.py log-agent --model M --task ID [--status ok|failed] [--seconds N] [--log FILE]
    python mmo_score.py council-note --task ID --agreed|--split [--log FILE]

A task is the MMO_TASK label. For each lane: the runs, the runs that ended ok, and the tasks whose
FIRST check passed, which is the number that says whether a lane can carry a kind of work.
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys
from collections import OrderedDict


def score(lines):
    lanes = OrderedDict()   # "provider/model" -> counters
    last_lane = {}          # task -> lane of its latest run
    checks_seen = {}        # task -> number of checks so far
    for line in lines:
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        task = ev.get("task") or ""
        if ev.get("kind") == "run":
            lane = "%s/%s" % (ev.get("provider"), ev.get("model"))
            c = lanes.setdefault(lane, {"runs": 0, "ok": 0, "seconds": 0, "checked": 0, "first_pass": 0, "bad": {}})
            c["runs"] += 1
            c["seconds"] += int(ev.get("seconds") or 0)
            if ev.get("status") == "ok":
                c["ok"] += 1
            else:
                c["bad"][ev.get("status")] = c["bad"].get(ev.get("status"), 0) + 1
            if task:
                last_lane[task] = lane
        elif ev.get("kind") == "check" and task in last_lane:
            n = checks_seen.get(task, 0)
            checks_seen[task] = n + 1
            if n == 0:   # only the first check of a task counts toward first-try pass
                c = lanes[last_lane[task]]
                c["checked"] += 1
                if ev.get("status") == "pass":
                    c["first_pass"] += 1
    return lanes


def print_table(lanes):
    print("%-44s %5s %5s %11s %6s  %s" % ("LANE", "RUNS", "OK", "FIRST-PASS", "AVG S", "NOT OK"))
    for lane, c in lanes.items():
        fp = "%d/%d" % (c["first_pass"], c["checked"]) if c["checked"] else "-"
        bad = " ".join("%s=%d" % kv for kv in sorted(c["bad"].items()))
        print("%-44s %5d %5d %11s %6d  %s" % (lane, c["runs"], c["ok"], fp, c["seconds"] // max(c["runs"], 1), bad))


# ---- tiers: the table lives in mmo_tiers.py (shared with mmo-roster). -------------------------------
# An id the table does not know stays "unknown tier" here: no tier advice rather than a guess.
from mmo_tiers import TIERS, tier_of as _tier_of


def tier_of(provider, model):
    tier = _tier_of(provider, model, default=False)
    return "unknown tier" if tier == "unknown" else tier


def read_events(path):
    out = []
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if isinstance(ev, dict):
                out.append(ev)
    return out


def is_claude(provider):
    return provider in ("claude-agent", "claude")


def council_summary(events):
    ran = sum(1 for e in events if e.get("kind") == "council")
    notes = [e for e in events if e.get("kind") == "council_note"]
    agreed = sum(1 for e in notes if e.get("agreed"))
    split = len(notes) - agreed
    lines = ["councils run: %d, noted: %d agreed, %d split" % (ran, agreed, split)]
    if len(notes) >= 5 and agreed * 100 >= 80 * len(notes):
        lines.append("The panel mostly confirmed the first answer (%d of %d): it could be used less." % (agreed, len(notes)))
    return lines


def share(events):
    runs = [e for e in events if e.get("kind") == "run"]
    lines = []
    if runs:
        fam = OrderedDict()
        for e in runs:
            name = "Claude" if is_claude(e.get("provider")) else str(e.get("provider"))
            c = fam.setdefault(name, [0, 0])
            c[0] += 1
            c[1] += int(e.get("seconds") or 0)
        total_s = sum(c[1] for c in fam.values())
        lines.append("%-24s %5s %7s %8s %7s" % ("FAMILY", "RUNS", "RUN %", "SECONDS", "SEC %"))
        for name, (n, sec) in sorted(fam.items(), key=lambda kv: -kv[1][0]):
            lines.append("%-24s %5d %6d%% %8d %6s" % (
                name, n, round(100.0 * n / len(runs)), sec, ("%d%%" % round(100.0 * sec / total_s)) if total_s else "-"))
        claude_n = fam.get("Claude", [0, 0])[0]
        answered = sorted({str(e.get("provider")) for e in runs
                           if not is_claude(e.get("provider")) and e.get("status") == "ok"})
        if len(runs) >= 10 and claude_n * 100 > 80 * len(runs) and answered:
            lines.append("Most work went to Claude although these lanes answered: %s." % ", ".join(answered))
    else:
        lines.append("no runs in the log")
    return lines + council_summary(events)


def task_report(events, task):
    lane = None
    rows, failed_checks = [], {}
    last = None
    for e in events:
        if e.get("task") != task:
            continue
        if e.get("kind") == "run":
            lane = "%s/%s" % (e.get("provider"), e.get("model"))
            last = (e.get("provider"), e.get("model"), e.get("status"))
            rows.append("run    %-40s %-8s %ss" % (lane, e.get("status"), int(e.get("seconds") or 0)))
        elif e.get("kind") == "check":
            rows.append("check  %s" % e.get("status"))
            if e.get("status") != "pass" and lane:
                failed_checks[lane] = failed_checks.get(lane, 0) + 1
    if not rows:
        return ["no history for task %s" % task]
    out = rows + ["failed checks: %d" % sum(failed_checks.values())]
    provider, model, status = last or (None, None, None)
    cur = "%s/%s" % (provider, model)
    tier = tier_of(provider, model) if last else "unknown tier"
    n = failed_checks.get(cur, 0)
    if status in ("limit", "auth", "model"):
        out.append("advice: %s on %s; use another lane of the same tier (%s), not a tier up." % (status, cur, tier))
    elif status == "base":
        out.append("advice: the lane started from the wrong base; recreate the worktree from the current branch and run again.")
    elif tier == "unknown tier":
        out.append("advice: unknown tier for %s; no tier advice (add it to mmo_tiers.py)." % cur)
    elif n >= 2:
        up = TIERS.index(tier) + 1
        if up < len(TIERS):
            out.append("advice: %d failed checks on %s (%s); go one tier up (%s) with the check output in the brief." % (n, cur, tier, TIERS[up]))
        else:
            out.append("advice: %d failed checks on %s, already the top tier; split the task or do it yourself." % (n, cur))
    else:
        out.append("advice: %d failed check(s) on %s (%s); retry on the same tier with the check output in the brief." % (n, cur, tier))
    return out


MIN_ROUTE_N = 5


def routes(lanes):
    by_tier = OrderedDict((t, []) for t in TIERS + ["unknown tier"])
    for lane, c in lanes.items():
        provider, _, model = lane.partition("/")
        by_tier[tier_of(provider, model)].append((lane, c))
    out = []
    for tier, items in by_tier.items():
        items = [(l, c) for l, c in items if c["checked"]]
        if not items:
            continue
        out.append("%s:" % tier)
        ranked = sorted([(l, c) for l, c in items if c["checked"] >= MIN_ROUTE_N],
                        key=lambda lc: (-lc[1]["first_pass"] / lc[1]["checked"], -lc[1]["checked"]))
        for i, (l, c) in enumerate(ranked, 1):
            out.append("  %d. %-40s %d/%d first-try (%d%%)" % (i, l, c["first_pass"], c["checked"],
                                                          round(100.0 * c["first_pass"] / c["checked"])))
        for l, c in items:
            if c["checked"] < MIN_ROUTE_N:
                out.append("  -  %-40s not enough data (n=%d)" % (l, c["checked"]))
    return out or ["no checked tasks in the log"]


def long_reports(directory, limit):
    out = []
    for path in sorted(glob.glob(os.path.join(directory, "**", "*.md"), recursive=True)):
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                text = f.read().splitlines()
        except OSError:
            continue
        if not text or not re.match(r"<!-- mmo ", text[0]):
            continue
        body = text[1:]
        while body and not body[-1].strip():
            body.pop()
        if len(body) > limit:
            m = re.search(r"provider=(\S+) model=(\S+)", text[0])
            out.append((len(body), "%s/%s" % m.groups() if m else "?", path))
    out.sort(reverse=True)
    return ["%-40s %5d lines  %s" % (lane, n, path) for n, lane, path in out] or \
           ["no lane output longer than %d lines" % limit]


def append_event(path, ev):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    ev = dict(ts=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), **ev)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(ev, separators=(",", ":")) + "\n")


def main(argv):
    if argv and argv[0] == "log-agent":
        ap = argparse.ArgumentParser(prog="mmo-score log-agent")
        ap.add_argument("--model", required=True)
        ap.add_argument("--task", required=True)
        ap.add_argument("--status", default="ok", choices=["ok", "failed", "timeout", "limit", "auth", "model"])
        ap.add_argument("--seconds", type=int, default=0)
        ap.add_argument("--log", default=os.environ.get("MMO_LOG"))
        a = ap.parse_args(argv[1:])
        if not a.log:
            ap.error("set MMO_LOG or pass --log FILE")
        append_event(a.log, {"kind": "run", "provider": "claude-agent", "model": a.model, "mode": "rw",
                             "status": a.status, "seconds": a.seconds, "task": a.task})
        return 0
    if argv and argv[0] == "council-note":
        ap = argparse.ArgumentParser(prog="mmo-score council-note")
        ap.add_argument("--task", required=True)
        g = ap.add_mutually_exclusive_group(required=True)
        g.add_argument("--agreed", action="store_true")
        g.add_argument("--split", action="store_true")
        ap.add_argument("--log", default=os.environ.get("MMO_LOG"))
        a = ap.parse_args(argv[1:])
        if not a.log:
            ap.error("set MMO_LOG or pass --log FILE")
        append_event(a.log, {"kind": "council_note", "task": a.task, "agreed": bool(a.agreed)})
        return 0

    ap = argparse.ArgumentParser(prog="mmo-score")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--share", action="store_true")
    ap.add_argument("--routes", action="store_true")
    ap.add_argument("--councils", action="store_true")
    ap.add_argument("--task")
    ap.add_argument("--cost", action="store_true")
    ap.add_argument("--prices")
    ap.add_argument("--reports")
    ap.add_argument("--lines", type=int, default=40)
    a = ap.parse_args(argv)
    if a.reports:
        print("\n".join(long_reports(a.reports, a.lines)))
        return 0
    path = a.file or os.environ.get("MMO_LOG")
    if not path or not os.path.isfile(path):
        sys.stderr.write("usage: mmo-score FILE (or set MMO_LOG)\n")
        return 2
    events = read_events(path)
    if a.share:
        out = share(events)
    elif a.councils:
        out = council_summary(events)
    elif a.cost:
        import mmo_cost
        out = mmo_cost.report(events, a.prices or mmo_cost.default_prices_path())
    elif a.task:
        out = task_report(events, a.task)
    elif a.routes:
        out = routes(score(json.dumps(e) for e in events))
    else:
        print_table(score(json.dumps(e) for e in events))
        return 0
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
