#!/usr/bin/env python3
"""Helper for mmo-advise: build the brief, read the advisor's answer, keep the budget.

    python mmo_advise.py brief --moment plan|stuck|done --question FILE --templates DIR --out FILE
                               [--evidence [head:|tail:]FILE]... [--diff-file FILE --diff-ref REF]
                               [--max-lines N] [--evidence-cap N] [--diff-cap N] [--question-cap N]
    python mmo_advise.py parse --answer FILE --max-lines N --max-chars N --out FILE [--full FILE]
    python mmo_advise.py budget take|refund|status --state FILE --session ID --budget N --budget-chars N
                               [--moment M] [--chars N]

`brief` prints the length of the finished brief in characters. `budget` keeps the count and the
characters sent per session, behind a lock directory, so two parallel calls cannot both pass.

Exit codes: 0 ok | 2 usage or refused input (secret-looking text) | 10 over budget (count or
characters) | 11 the answer has no verdict line (unusable).
"""
import argparse
import json
import os
import re
import sys
import time

# Why: the brief goes to another vendor. These are the shapes real keys have; pure hex (commit ids,
# checksums) is left alone so that ordinary diffs and logs are not refused.
SECRET_RES = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"\bak_[A-Za-z0-9]{16,}"),
    re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"\bAIza[0-9A-Za-z_-]{30,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\b(?:api[_-]?key|secret|token|passw(?:or)?d)\b\s*[:=]\s*['\"]?[A-Za-z0-9+/_-]{12,}(?=['\"\s,;]|$)"),
]
LONG_TOKEN = re.compile(r"[A-Za-z0-9+/_-]{32,}")
HEXISH = re.compile(r"^[0-9a-fA-F-]+$")
HASH_PREFIX = re.compile(r"(?i)sha\d*[-:]$")

VERDICT = re.compile(r"^(PROCEED)[.!]?$|^(CHANGE|STOP)\s*:\s*(\S.*)$", re.I)
MAX_LINE = 300

MEANING = {
    "plan": "PROCEED = the approach is sound, start. CHANGE = start, but with this one change. "
            "STOP = this approach will not get there; say why.",
    "stuck": "PROCEED = the current line of attack is right, keep going. CHANGE = try this instead. "
             "STOP = the task as set cannot work; say why.",
    "done": "PROCEED = it does what was asked, it is done. CHANGE = one thing is left to fix. "
            "STOP = it does not do what was asked.",
}

RULES = """## Rules for your answer

- I am the executor: I do the work and talk to the user. You are the advisor: you only advise.
  Do not use tools, do not read or change files, and do not ask me questions. If something is
  missing, say what you assumed and go on.
- Answer from this brief alone. Mark anything you cannot see in it as a guess.
- The first line is exactly one of these three:
  PROCEED
  CHANGE: <the one change, in one line>
  STOP: <the reason, in one line>
  {meaning}
- Then at most {max_lines} lines of reasons, one per line, each tied to evidence in this brief
  (quote it, or name the file, line or step). No preamble, no headings, no summary.
- Keep the whole answer to at most {max_lines} lines and about {max_chars_round} characters in
  total, verdict line included. Longer answers are cut, so put the most important thing first.
- If nothing is wrong, say PROCEED and name the one risk worth watching. Do not invent a problem.
"""


def looks_secret(line):
    for rx in SECRET_RES:
        if rx.search(line):
            return True
    for m in LONG_TOKEN.finditer(line):
        tok = m.group(0)
        if HEXISH.match(tok) or HASH_PREFIX.search(line[: m.start()]):
            continue
        if re.search(r"[a-z]", tok) and re.search(r"[A-Z]", tok) and re.search(r"[0-9]", tok):
            return True
    return False


def secret_lines(text):
    return sum(1 for ln in text.splitlines() if looks_secret(ln))


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def keep_head(text, n):
    if len(text) <= n:
        return text, False
    cut = text[:n]
    nl = cut.rfind("\n")
    if nl > n - 200:
        cut = cut[:nl]
    return cut, True


def keep_tail(text, n):
    if len(text) <= n:
        return text, False
    cut = text[-n:]
    nl = cut.find("\n")
    if 0 <= nl < 200:
        cut = cut[nl + 1:]
    return cut, True


def evidence_spec(spec):
    """head:FILE or tail:FILE, else guess: logs and command output keep their tail."""
    for side in ("head", "tail"):
        if spec.startswith(side + ":"):
            return side, spec[len(side) + 1:]
    name = os.path.basename(spec).lower()
    tail = name.endswith((".log", ".out", ".err")) or re.search(r"log|err|out|trace|stderr|stdout", name)
    return ("tail" if tail else "head"), spec


def build_evidence(specs, cap):
    items = []
    for spec in specs:
        side, path = evidence_spec(spec)
        if not os.path.isfile(path):
            die("evidence file not found: " + path)
        items.append([side, path, read(path)])
    if not items:
        return "(none given)"
    # Smallest first, so a short spec is never cut to make room for a long log.
    order = sorted(range(len(items)), key=lambda i: len(items[i][2]))
    left, budget = len(items), cap
    blocks = [None] * len(items)
    for i in order:
        side, path, text = items[i]
        share = budget // left
        kept, cut = (keep_tail if side == "tail" else keep_head)(text, share)
        budget -= len(kept)
        left -= 1
        head = "### {} ({} of {} characters, {} kept)".format(os.path.basename(path), len(kept), len(text), side)
        note = ""
        if cut:
            where = "the start was cut, the tail is kept" if side == "tail" else "the end was cut, the head is kept"
            note = "\n[truncated by mmo-advise: {} characters left out; {}]".format(len(text) - len(kept), where)
        blocks[i] = "{}\n```\n{}\n```{}".format(head, kept.rstrip("\n"), note)
    return "\n\n".join(blocks)


def die(msg, code=2):
    print("mmo-advise: " + msg, file=sys.stderr)
    sys.exit(code)


def cmd_brief(a):
    tpl_path = os.path.join(a.templates, "advise-{}.md".format(a.moment))
    if not os.path.isfile(tpl_path):
        die("template missing: advise-{}.md".format(a.moment))
    question = read(a.question)
    inputs = [("question " + os.path.basename(a.question), question)]
    for spec in a.evidence:
        _, path = evidence_spec(spec)
        if os.path.isfile(path):
            inputs.append(("evidence " + os.path.basename(path), read(path)))
    diff = read(a.diff_file) if a.diff_file else ""
    if a.diff_file:
        inputs.append(("diff against " + a.diff_ref, diff))
    refused = [(name, n) for name, n in ((nm, secret_lines(t)) for nm, t in inputs) if n]
    if refused:
        for name, n in refused:
            print("mmo-advise: {}: {} line(s) look like a secret (key-like token); refused. "
                  "Remove them or pass a redacted copy.".format(name, n), file=sys.stderr)
        sys.exit(2)

    q, qcut = keep_head(question, a.question_cap)
    if qcut:
        q += "\n[truncated by mmo-advise: the question was cut to {} characters]".format(len(q))
    if a.diff_file:
        if not diff.strip():
            d = "(git diff {} is empty)".format(a.diff_ref)
        else:
            kept, cut = keep_head(diff, a.diff_cap)
            d = "`git diff {}`:\n```diff\n{}\n```".format(a.diff_ref, kept.rstrip("\n"))
            if cut:
                d += "\n[truncated by mmo-advise: showed {} of {} characters of the diff; the rest was cut]".format(
                    len(kept), len(diff))
    else:
        d = "(no diff attached; see the evidence)"
    body = read(tpl_path)
    body = body.replace("{{QUESTION}}", q.rstrip("\n"))
    body = body.replace("{{EVIDENCE}}", build_evidence(a.evidence, a.evidence_cap))
    body = body.replace("{{DIFF}}", d)
    body = body.rstrip("\n") + "\n\n" + RULES.format(meaning=MEANING[a.moment], max_lines=a.max_lines,
                                                     max_chars_round=max(100, a.max_chars - a.max_chars // 14))
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)
    print(len(body))
    return 0


def cut_at_end(text, cap):
    """Cut text to at most cap characters, at the last line end or sentence end; hard cut if none."""
    head = text[:cap]
    best = head.rfind("\n")
    for m in re.finditer(r"[.!?](?=\s|$)", head):
        best = max(best, m.end())
    if best < cap // 3:  # a tiny stub is worse than a hard cut
        return head.rstrip()
    return head[:best].rstrip()


def cmd_parse(a):
    raw = read(a.answer)
    if a.full:
        os.makedirs(os.path.dirname(os.path.abspath(a.full)), exist_ok=True)
        with open(a.full, "w", encoding="utf-8", newline="\n") as f:
            f.write(raw if raw.endswith("\n") else raw + "\n")
    lines = raw.splitlines()
    verdict, at = None, -1
    for i, ln in enumerate(lines):
        s = re.sub(r"^[\s#>*`_-]*", "", ln)
        s = re.sub(r"[\s*`_]*$", "", s)
        s = re.sub(r"(?i)^verdict\s*:\s*", "", s)
        m = VERDICT.match(s)
        if m:
            if m.group(1):
                verdict = "PROCEED"
            else:
                verdict = "{}: {}".format(m.group(2).upper(), m.group(3).strip()[:MAX_LINE])
            at = i
            break
    if verdict is None:
        print("unusable")
        return 11
    notes = []
    if any(ln.strip() for ln in lines[:at]):
        notes.append("[mmo-advise: dropped {} line(s) before the verdict]".format(
            sum(1 for ln in lines[:at] if ln.strip())))
    reasons = []
    long_cut = 0
    for ln in lines[at + 1:]:
        s = ln.strip()
        if not s or re.match(r"^(```|---+|#+\s*$)", s):
            continue
        if len(s) > MAX_LINE:
            s = s[:MAX_LINE].rstrip() + " ..."
            long_cut += 1
        reasons.append(s)
    extra = len(reasons) - a.max_lines
    if extra > 0:
        reasons = reasons[: a.max_lines]
        notes.append("[mmo-advise: trimmed {} line(s) over the limit of {}]".format(extra, a.max_lines))
    if long_cut:
        notes.append("[mmo-advise: shortened {} line(s) to {} characters]".format(long_cut, MAX_LINE))
    body = "\n".join([verdict] + reasons)
    if a.max_chars > 0 and len(body) > a.max_chars:
        kept = cut_at_end(body, a.max_chars)
        if len(kept) <= len(verdict):
            kept = verdict  # the verdict line is never cut
        notes.append("[mmo-advise: cut {} characters over the limit of {}{}]".format(
            len(body) - len(kept), a.max_chars,
            "; the full answer is in " + a.full if a.full else ""))
        body = kept
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join([body] + notes) + "\n")
    print("{}\t{}".format(verdict.split(":")[0], "yes" if notes else "no"))
    return 0


def load_state(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict) and isinstance(data.get("sessions"), dict):
            for k in ("chars", "moments"):
                if not isinstance(data.get(k), dict):
                    data[k] = {}
            return data
    except (OSError, ValueError):
        pass
    return {"sessions": {}, "chars": {}, "moments": {}}


class Lock:
    """An atomic lock: os.mkdir either creates the folder or fails, on Windows and POSIX alike.
    Held only around read, check and write of the state file, never while a lane runs."""

    def __init__(self, state, wait=5.0, stale=60.0):
        self.path = os.path.abspath(state) + ".lock"
        self.wait, self.stale = wait, stale

    def __enter__(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        end = time.time() + self.wait
        while True:
            try:
                os.mkdir(self.path)
                return self
            except FileExistsError:
                pass
            try:
                age = time.time() - os.path.getmtime(self.path)
            except OSError:
                continue  # it vanished between the two calls: try again at once
            if age > self.stale:
                print("mmo-advise: warning: breaking a stale lock ({:.0f} s old): {}".format(age, self.path),
                      file=sys.stderr)
                try:
                    os.rmdir(self.path)
                except OSError:
                    pass
                continue
            if time.time() > end:
                die("could not get the budget lock {} within {:.0f} s; if no other mmo-advise is running, "
                    "remove that folder".format(self.path, self.wait))
            time.sleep(0.05)

    def __exit__(self, *exc):
        try:
            os.rmdir(self.path)
        except OSError:
            pass
        return False


def save_state(path, st):
    # Through a temp file and os.replace, so a crash cannot leave half a file.
    tmp = "{}.{}.tmp".format(path, os.getpid())
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, indent=1, sort_keys=True)
        f.write("\n")
    os.replace(tmp, path)


def cmd_budget(a):
    with Lock(a.state):
        st = load_state(a.state)
        sid = a.session
        used = int(st["sessions"].get(sid, 0))
        chars = int(st["chars"].get(sid, 0))
        moments = st["moments"].get(sid) or {}
        if a.action == "status":
            of = "" if a.budget_chars == 0 else " of {}".format(a.budget_chars)
            left = "unlimited" if a.budget_chars == 0 else "{} left".format(max(0, a.budget_chars - chars))
            print("session: {}".format(sid))
            print("consultations: {} used of {}, {} left".format(used, a.budget, max(0, a.budget - used)))
            print("characters sent: {} used{}, {}".format(chars, of, left))
            print("moments: " + ", ".join("{} {}".format(m, int(moments.get(m, 0))) for m in ("plan", "stuck", "done")))
            return 0
        if a.action == "take":
            if used >= a.budget:
                print("mmo-advise: budget used up: {} of {} consultations in session {}. Decide without the "
                      "advisor, or raise it on purpose (--budget N or MMO_ADVISE_BUDGET).".format(used, a.budget, sid),
                      file=sys.stderr)
                return 10
            if a.budget_chars and chars + a.chars > a.budget_chars:
                print("mmo-advise: character budget used up: this brief is {} characters, {} of {} already sent in "
                      "session {} ({} left). Send a smaller --diff or less evidence, or raise it on purpose "
                      "(--budget-chars N or MMO_ADVISE_BUDGET_CHARS).".format(
                          a.chars, chars, a.budget_chars, sid, max(0, a.budget_chars - chars)), file=sys.stderr)
                return 10
            used += 1
            chars += a.chars
            if a.moment:
                moments[a.moment] = int(moments.get(a.moment, 0)) + 1
        else:
            used = max(0, used - 1)
            chars = max(0, chars - a.chars)
            if a.moment:
                moments[a.moment] = max(0, int(moments.get(a.moment, 0)) - 1)
        st["sessions"][sid] = used
        st["chars"][sid] = chars
        st["moments"][sid] = moments
        save_state(a.state, st)
    print("{} {} {}".format(used, a.budget, chars))
    return 0


def main():
    p = argparse.ArgumentParser(prog="mmo_advise.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("brief")
    b.add_argument("--moment", choices=sorted(MEANING), required=True)
    b.add_argument("--question", required=True)
    b.add_argument("--templates", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--evidence", action="append", default=[])
    b.add_argument("--diff-file")
    b.add_argument("--diff-ref", default="")
    b.add_argument("--max-lines", type=int, default=12)
    b.add_argument("--max-chars", type=int, default=1500)
    b.add_argument("--evidence-cap", type=int, default=12000)
    b.add_argument("--diff-cap", type=int, default=10000)
    b.add_argument("--question-cap", type=int, default=4000)
    r = sub.add_parser("parse")
    r.add_argument("--answer", required=True)
    r.add_argument("--max-lines", type=int, default=12)
    r.add_argument("--max-chars", type=int, default=1500)
    r.add_argument("--full")
    r.add_argument("--out", required=True)
    g = sub.add_parser("budget")
    g.add_argument("action", choices=["take", "refund", "status"])
    g.add_argument("--moment", default="")
    g.add_argument("--chars", type=int, default=0)
    g.add_argument("--budget-chars", type=int, default=60000)
    g.add_argument("--state", required=True)
    g.add_argument("--session", required=True)
    g.add_argument("--budget", type=int, default=6)
    a = p.parse_args()
    return {"brief": cmd_brief, "parse": cmd_parse, "budget": cmd_budget}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
