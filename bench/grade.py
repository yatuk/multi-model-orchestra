"""Grade one lane's result for one task. Prints `score<TAB>detail`, score 0..1.

    python grade.py bugfix    WORKTREE
    python grade.py reasoning ANSWER_FILE
    python grade.py bulk      ANSWER_FILE
    python grade.py multifile WORKTREE
    python grade.py refactor  WORKTREE
    python grade.py spec      ANSWER_FILE
    python grade.py service   WORKTREE

A write task (bugfix, multifile, refactor, service) also takes --lane-out FILE, the lane's
mmo-run result file. Then a lane whose status is not ok, or whose last line says FAILED or
BLOCKED, is still graded on what it left in the worktree, with that fact first in the detail;
it gets 0 only when the worktree has no changes.

multifile, refactor and service are graded in a fresh directory that holds only the lane's package
and the grader's own copies of the visible and hidden tests, never the lane's test files.
"""
import ast
import contextlib
import csv
import io
import os
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
TASKS = HERE / "tasks"


def body(path):
    text = Path(path).read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if lines and lines[0].startswith("<!-- mmo"):
        if "status=ok" not in lines[0]:
            return None
        lines = lines[1:]
    return "\n".join(lines)


def run_tests(wt, module):
    r = subprocess.run([sys.executable, "-m", "unittest", "-q", module], cwd=wt,
                       capture_output=True, text=True, timeout=120)
    out = r.stderr + r.stdout
    m = re.search(r"Ran (\d+) test", out)
    ran = int(m.group(1)) if m else 0
    f = re.search(r"failures=(\d+)", out)
    e = re.search(r"errors=(\d+)", out)
    bad = (int(f.group(1)) if f else 0) + (int(e.group(1)) if e else 0)
    return ran, bad


def bugfix(wt):
    wt = Path(wt)
    visible = wt / "test_durations.py"
    tampered = not visible.exists() or visible.read_text(encoding="utf-8") != (TASKS / "bugfix" / "test_durations.py").read_text(encoding="utf-8")
    shutil.copy(TASKS / "bugfix" / "hidden_test_durations.py", wt / "hidden_test_durations.py")
    ran_v, bad_v = run_tests(wt, "test_durations")
    ran_h, bad_h = run_tests(wt, "hidden_test_durations")
    if tampered:
        return 0.0, "visible tests were edited (rule broken)"
    if ran_v == 0 or bad_v:
        return 0.0, f"visible tests fail ({bad_v}/{ran_v})"
    score = (ran_h - bad_h) / ran_h if ran_h else 0.0
    return score, f"visible ok, hidden {ran_h - bad_h}/{ran_h}"


def gold_reasoning():
    src = (TASKS / "reasoning" / "brief.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", src, re.S)
    gold = {}
    for key, code in zip(("q1", "q2"), blocks):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            exec(code, {})
        gold[key] = int(buf.getvalue().strip())
    gold["q3"] = sum(1 for n in range(1, 1001) if (n % 3 == 0 or n % 5 == 0) and n % 15 != 0)
    return gold


def reasoning(path):
    text = body(path)
    if text is None:
        return 0.0, "lane failed"
    m = re.search(r"\{[^{}]*\}", text)
    if not m:
        return 0.0, "no JSON"
    try:
        got = json.loads(m.group(0))
    except json.JSONDecodeError:
        return 0.0, "bad JSON"
    gold = gold_reasoning()
    right = [k for k in gold if str(got.get(k)).strip() == str(gold[k])]
    return len(right) / len(gold), f"{len(right)}/{len(gold)} (gold {gold}, got {got})"


def bulk(path):
    text = body(path)
    if text is None:
        return 0.0, "lane failed"
    text = re.sub(r"^```\w*\n|```\s*$", "", text.strip(), flags=re.M)
    gold = {r["line"]: r["label"] for r in csv.DictReader(open(TASKS / "bulk" / "gold.csv", encoding="utf-8"))}
    got = {}
    for row in csv.reader(io.StringIO(text)):
        if len(row) >= 2 and row[0].strip().isdigit():
            got[row[0].strip()] = row[1].strip().upper()
    right = sum(1 for k, v in gold.items() if got.get(k) == v)
    misses = [k for k, v in gold.items() if got.get(k) != v]
    return right / len(gold), f"{right}/{len(gold)} correct" + (f", wrong lines {','.join(misses[:12])}" if misses else "")


# Write tasks with a package, visible tests (given to the lane) and hidden tests (never given).
RW_TASKS = {
    "multifile": {"package": "parcel", "visible": ["test_parcel.py"], "hidden": ["hidden_test_parcel.py"]},
    "refactor": {"package": "evlog", "visible": ["test_evlog.py"], "hidden": ["hidden_test_evlog.py"]},
    "service": {"package": "roombook", "visible": ["test_roombook.py"], "hidden": ["hidden_test_roombook.py"]},
}


def expected_tests(path):
    """Test ids in a test file, read from its source, grouped by class in file order.

    Counting from the source means a module that fails to import, or a test the lane's code
    hides, still counts as a failed test instead of shrinking the total.
    """
    mod = Path(path).stem
    groups = {}
    for node in ast.parse(Path(path).read_text(encoding="utf-8")).body:
        if isinstance(node, ast.ClassDef):
            tests = [f"{mod}.{node.name}.{f.name}" for f in node.body
                     if isinstance(f, ast.FunctionDef) and f.name.startswith("test")]
            if tests:
                groups[node.name] = tests
    return groups


def same_text(a, b):
    # Line endings may change on checkout (core.autocrlf); content may not.
    def read(p):
        return Path(p).read_bytes().replace(b"\r\n", b"\n")

    return read(a) == read(b)


def run_isolated(task, wt):
    """Copy the lane's package and pristine tests to a fresh directory and run them there."""
    cfg, tdir = RW_TASKS[task], TASKS / task
    with tempfile.TemporaryDirectory() as work, tempfile.TemporaryDirectory() as out:
        work = Path(work)
        shutil.copytree(Path(wt) / cfg["package"], work / cfg["package"],
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for name in cfg["visible"]:
            shutil.copy(tdir / "start" / name, work / name)
        for name in cfg["hidden"]:
            shutil.copy(tdir / "hidden" / name, work / name)
        result = Path(out) / "result.json"
        modules = [Path(n).stem for n in cfg["hidden"] + cfg["visible"]]
        try:
            subprocess.run([sys.executable, "-I", str(HERE / "hidden_runner.py"), str(work), str(result), *modules],
                           cwd=work, capture_output=True, text=True, timeout=300,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        except subprocess.TimeoutExpired:
            return None, "tests timed out"
        if not result.exists():
            return None, "test runner wrote no result (the package exited or crashed the interpreter)"
        return json.loads(result.read_text(encoding="utf-8")), ""


def graded_rw(task, wt):
    cfg, tdir, wt = RW_TASKS[task], TASKS / task, Path(wt)
    deleted = [n for n in cfg["visible"] if not (wt / n).exists()]
    edited = [n for n in cfg["visible"] if (wt / n).exists() and not same_text(wt / n, tdir / "start" / n)]
    if not (wt / cfg["package"]).is_dir():
        return 0.0, f"package {cfg['package']}/ is missing"
    res, err = run_isolated(task, wt)
    if res is None:
        return 0.0, err
    outcome = res["outcome"]

    def tally(files, folder):
        parts, passed, total = [], 0, 0
        for name in files:
            for group, ids in expected_tests(tdir / folder / name).items():
                ok = sum(1 for i in ids if outcome.get(i) == "pass")
                parts.append(f"{group} {ok}/{len(ids)}")
                passed, total = passed + ok, total + len(ids)
        return passed, total, parts

    hp, ht, groups = tally(cfg["hidden"], "hidden")
    vp, vt, _ = tally(cfg["visible"], "start")
    score = hp / ht if ht else 0.0
    detail = f"hidden {hp}/{ht} ({', '.join(groups)}), visible {vp}/{vt}"
    if res["missing"]:
        detail += f"; public names missing: {', '.join(res['missing'])}"
    if edited or deleted:
        what = "; ".join(x for x in (f"visible test edited: {', '.join(edited)}" if edited else "",
                                       f"visible test deleted: {', '.join(deleted)}" if deleted else "") if x)
        return 0.0, f"{what} (rule broken, score capped at 0; graded on pristine tests: {detail})"
    return score, detail


def multifile(wt):
    return graded_rw("multifile", wt)


def refactor(wt):
    return graded_rw("refactor", wt)


def service(wt):
    return graded_rw("service", wt)


# --- lane status (bench3) ---
# A lane's own verdict is not the grade: the claude lane once reported FAILED on correct diffs
# because it could not run the tests. The work in the worktree is graded either way.
LAST_WORD = re.compile(r"^[\W_]*(DONE|FAILED|BLOCKED)\b")


def lane_report(path):
    """(status from the mmo header, DONE/FAILED/BLOCKED from the last non-empty line or None)."""
    p = Path(path)
    if not p.exists():
        return "missing", None
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    status = "unknown"
    if lines and lines[0].startswith("<!-- mmo"):
        m = re.search(r"status=(\w+)", lines[0])
        status = m.group(1) if m else "unknown"
        lines = lines[1:]
    for line in reversed(lines):
        if line.strip():
            m = LAST_WORD.match(line.strip())
            return status, (m.group(1) if m else None)
    return status, None


def worktree_changed(wt):
    """True when git sees changes other than bytecode. Not a git checkout: True (grade it)."""
    r = subprocess.run(["git", "-C", str(wt), "status", "--porcelain", "--untracked-files=all"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return True
    for line in r.stdout.splitlines():
        name = line[3:].strip().strip('"')
        if "__pycache__" not in name and not name.endswith(".pyc"):
            return True
    return False


def with_lane(task, wt, lane_out):
    status, word = lane_report(lane_out)
    if status != "ok":
        prefix, failed = f"lane status={status}; ", f"lane failed: {status}"
    elif word in ("FAILED", "BLOCKED"):
        prefix, failed = f"lane said {word}; ", f"lane said {word}"
    else:
        prefix = failed = ""
    if prefix and not worktree_changed(wt):
        return 0.0, f"{failed}, no changes"
    score, detail = GRADERS[task](wt)
    return score, prefix + detail
# --- end lane status ---


SPEC_LINE = re.compile(r"\s*(a\d\d)\s+(KEEP|ARCHIVE|DELETE)\s+([1-8])\s*")


def spec(path):
    if not Path(path).exists():
        return 0.0, "no answer file"
    text = body(path)
    if text is None:
        return 0.0, "lane failed"
    gold = {r["id"]: (r["decision"], r["rule"]) for r in csv.DictReader(open(TASKS / "spec" / "gold.csv", encoding="utf-8"))}
    got = {}
    for line in text.splitlines():
        m = SPEC_LINE.fullmatch(line)
        if m and m.group(1) not in got:
            got[m.group(1)] = (m.group(2), m.group(3))
    wrong = [k for k in gold if got.get(k) != gold[k]]
    right = len(gold) - len(wrong)
    shown = ", ".join(f"{k} got {' '.join(got[k]) if k in got else 'nothing'} want {' '.join(gold[k])}" for k in wrong[:8])
    return right / len(gold), f"{right}/{len(gold)} exact" + (f"; wrong: {shown}" if wrong else "")


GRADERS = {"bugfix": bugfix, "reasoning": reasoning, "bulk": bulk,
           "multifile": multifile, "refactor": refactor, "spec": spec, "service": service}
WRITE_TASKS = ("bugfix", "multifile", "refactor", "service")


def main():
    task, target = sys.argv[1], sys.argv[2]
    rest = sys.argv[3:]
    if rest[:1] == ["--lane-out"] and len(rest) == 2 and task in WRITE_TASKS:
        score, detail = with_lane(task, target, rest[1])
    else:
        score, detail = GRADERS[task](target)
    print(f"{score:.2f}\t{detail}")


if __name__ == "__main__":
    main()
