#!/usr/bin/env python3
"""Verified lessons: a capped JSON-lines log that can only be written with proof.

Why: a lesson is accepted only when a passing mmo-check report backs it, it is one
short sentence, and it goes stale on its own when the lane's adapter file changes.
Reads are capped at 5 so the output can be pasted straight into the next brief.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAX_TEXT = 240
MAX_SHOW = 5

# Why: a lesson is pasted into other briefs, so it must never carry credentials or personal paths.
SECRET_RES = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{3,}"),
    re.compile(r"\bak_[A-Za-z0-9]{3,}"),
    re.compile(r"\bghp_[A-Za-z0-9]{3,}"),
    re.compile(r"[A-Za-z0-9+/=]{32,}"),
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+\.[A-Za-z0-9.-]+"),
    re.compile(r"C:\\Users\\", re.I),
    re.compile(r"/Users/"),
    re.compile(r"/home/"),
]


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_path(args):
    return args.file or os.environ.get("MMO_LESSONS") or os.path.join(".mmo", "lessons.jsonl")


def providers_dir():
    return os.environ.get("MMO_PROVIDERS_DIR") or os.path.join(HERE, "providers")


def provider_of(lane):
    return lane.split("/", 1)[0]


def adapter_hash(lane):
    """Hash of the lane's adapter file, or '' for '*' or a missing file."""
    if lane == "*":
        return ""
    p = os.path.join(providers_dir(), provider_of(lane) + ".sh")
    try:
        with open(p, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()[:12]
    except OSError:
        return ""


def read_log(path):
    """Return (lessons in file order, set of dropped ids)."""
    lessons, dropped = [], set()
    if not os.path.isfile(path):
        return lessons, dropped
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
            except ValueError:
                continue
            if "drop" in o:
                dropped.add(o["drop"])
            elif "id" in o:
                lessons.append(o)
    return lessons, dropped


def append(path, obj):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


def num(lid):
    try:
        return int(lid[1:])
    except (ValueError, IndexError):
        return 0


def flags(lessons, dropped):
    """Map id -> 'ok' | 'stale' | 'superseded' | 'dropped'."""
    superseded = {l.get("supersedes") for l in lessons if l.get("supersedes")}
    out = {}
    for l in lessons:
        lid = l["id"]
        if lid in dropped:
            out[lid] = "dropped"
        elif lid in superseded:
            out[lid] = "superseded"
        elif l.get("adapter") and l["adapter"] != adapter_hash(l["lane"]):
            out[lid] = "stale"
        else:
            out[lid] = "ok"
    return out


def applies(lesson_lane, want):
    if lesson_lane == "*" or lesson_lane == want:
        return True
    return "/" not in lesson_lane and lesson_lane == provider_of(want)


def check_report(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            first = f.readline()
    except OSError:
        return False
    return bool(re.match(r"<!--\s*mmo-check\b.*\bstatus=pass\b", first))


def cmd_add(args):
    text = args.text
    if "\n" in text or "\r" in text:
        print("mmo-lessons: a lesson is one sentence, no newline", file=sys.stderr)
        return 2
    if len(text) > MAX_TEXT:
        print("mmo-lessons: text is %d characters, the limit is %d" % (len(text), MAX_TEXT), file=sys.stderr)
        return 2
    if not text.strip():
        print("mmo-lessons: empty text", file=sys.stderr)
        return 2
    for rx in SECRET_RES:
        if rx.search(text):
            print("mmo-lessons: text looks like a secret, email or private path; refused", file=sys.stderr)
            return 2
    if not check_report(args.check):
        print("mmo-lessons: %s is not an mmo-check report with status=pass; no lesson without proof" % args.check,
              file=sys.stderr)
        return 3
    path = log_path(args)
    lessons, _ = read_log(path)
    if args.supersedes and args.supersedes not in {l["id"] for l in lessons}:
        print("mmo-lessons: cannot supersede unknown id %s" % args.supersedes, file=sys.stderr)
        return 2
    lid = "L%d" % (max([num(l["id"]) for l in lessons] + [0]) + 1)
    append(path, {
        "id": lid,
        "ts": now(),
        "lane": args.lane,
        "text": text,
        "check": args.check,
        "adapter": adapter_hash(args.lane),
        "supersedes": args.supersedes or "",
    })
    print(lid)
    return 0


def cmd_show(args):
    n = max(0, min(args.n, MAX_SHOW))
    lessons, dropped = read_log(log_path(args))
    fl = flags(lessons, dropped)
    hits = [l for l in lessons if fl[l["id"]] == "ok" and applies(l["lane"], args.lane)]
    hits.sort(key=lambda l: num(l["id"]), reverse=True)
    for l in hits[:n]:
        print("- %s  [%s]" % (l["text"], l["id"]))
    return 0


def cmd_list(args):
    lessons, dropped = read_log(log_path(args))
    fl = flags(lessons, dropped)
    for l in lessons:
        f = fl[l["id"]]
        if f != "ok" and not args.all:
            continue
        print("%s\t%s\t%s\t%s\t%s" % (l["id"], l["lane"], l["ts"][:10], f, l["text"]))
    return 0


def cmd_drop(args):
    path = log_path(args)
    lessons, _ = read_log(path)
    if args.id not in {l["id"] for l in lessons}:
        print("mmo-lessons: unknown id %s" % args.id, file=sys.stderr)
        return 2
    append(path, {"drop": args.id, "ts": now()})
    print("dropped " + args.id)
    return 0


def main():
    # Why: the output is pasted into briefs; Windows text mode would add CRs.
    sys.stdout.reconfigure(newline="\n")
    ap = argparse.ArgumentParser(prog="mmo-lessons")
    ap.add_argument("--file", help="log file (default $MMO_LESSONS or .mmo/lessons.jsonl)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add")
    a.add_argument("--lane", required=True)
    a.add_argument("--text", required=True)
    a.add_argument("--check", required=True)
    a.add_argument("--supersedes", default="")
    s = sub.add_parser("show")
    s.add_argument("--lane", required=True)
    s.add_argument("-n", type=int, default=MAX_SHOW)
    li = sub.add_parser("list")
    li.add_argument("--all", action="store_true")
    d = sub.add_parser("drop")
    d.add_argument("id")
    # --file is accepted after the subcommand too
    for p in (a, s, li, d):
        p.add_argument("--file", default=argparse.SUPPRESS, help=argparse.SUPPRESS)
    args = ap.parse_args()
    if not hasattr(args, "file"):
        args.file = None
    return {"add": cmd_add, "show": cmd_show, "list": cmd_list, "drop": cmd_drop}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
