"""Grade one lane's result for one task. Prints `score<TAB>detail`, score 0..1.

    python grade.py bugfix    WORKTREE
    python grade.py reasoning ANSWER_FILE
    python grade.py bulk      ANSWER_FILE
"""
import contextlib
import csv
import io
import json
import re
import shutil
import subprocess
import sys
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
    tampered = (wt / "test_durations.py").read_text(encoding="utf-8") != (TASKS / "bugfix" / "test_durations.py").read_text(encoding="utf-8")
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


def main():
    task, target = sys.argv[1], sys.argv[2]
    score, detail = {"bugfix": bugfix, "reasoning": reasoning, "bulk": bulk}[task](target)
    print(f"{score:.2f}\t{detail}")


if __name__ == "__main__":
    main()
