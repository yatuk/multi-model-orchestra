"""What the lanes cost, from the numbers the tools reported. Stdlib only; used by `mmo-score --cost`.

Reads the run lines mmo-run writes to $MMO_LOG (tokens_in, tokens_out, tokens_cached, cost_usd) and the
check lines mmo-check writes. Per lane: runs, runs with a reported cost, the sum of reported cost, the
tokens, and the cost per PASSED task.

Cost per passed task: the reported cost of every labelled run of the lane (retries and failed tasks
included) divided by the number of tasks whose check passed while that lane was the latest one working
on them. A task that moved on to another lane after failures leaves its cost on the first lane and its
pass on the last. Runs with no reported cost are counted, never treated as free: the per-pass figure only
covers the costed runs and says so.

Prices are optional and yours (see skills/orchestra/prices.example). With a matching line, a run that
has tokens but no reported cost gets a computed cost, kept in its own column and marked "~". Reported and
estimated sums are never added into one unmarked number.
"""
import fnmatch
import os
import sys
from collections import OrderedDict


def default_prices_path():
    env = os.environ.get("MMO_PRICES")
    if env:
        return env
    home = os.environ.get("HOME") or os.path.expanduser("~")  # HOME first: tests fake it
    path = os.path.join(home, ".config", "mmo", "prices")
    return path if os.path.isfile(path) else ""


def read_prices(path):
    """([(pattern, in_per_million, out_per_million, cached_per_million or None)], count of bad lines)."""
    rows, bad = [], 0
    if not path:
        return rows, bad
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.split("#", 1)[0].split()
            if not parts:
                continue
            try:
                nums = [float(x) for x in parts[1:]]
                if not 2 <= len(nums) <= 3 or any(n < 0 for n in nums):
                    raise ValueError
            except ValueError:
                bad += 1
                continue
            rows.append((parts[0].lower(), nums[0], nums[1], nums[2] if len(nums) == 3 else None))
    return rows, bad


def estimate(prices, lane, tokens):
    """Cost in USD from the first matching price line, or None. Needs both token counts; cached tokens
    count only when the line has a cached price."""
    if "tokens_in" not in tokens or "tokens_out" not in tokens:
        return None
    for pattern, pin, pout, pcached in prices:
        if fnmatch.fnmatchcase(lane.lower(), pattern):
            cost = tokens["tokens_in"] * pin / 1e6 + tokens["tokens_out"] * pout / 1e6
            if pcached is not None and tokens.get("tokens_cached"):
                cost += tokens["tokens_cached"] * pcached / 1e6
            return cost
    return None


def _num(x):
    return x if isinstance(x, (int, float)) and not isinstance(x, bool) and x >= 0 else None


def tally(events, prices=()):
    lanes = OrderedDict()
    last_lane = {}   # task -> lane of its latest run
    for ev in events:
        task = ev.get("task") or ""
        if ev.get("kind") == "run":
            lane = "%s/%s" % (ev.get("provider"), ev.get("model"))
            c = lanes.setdefault(lane, {"runs": 0, "costed": 0, "reported": 0.0, "estimated": 0.0, "est_runs": 0,
                                        "tin": 0, "tout": 0, "tok_runs": 0, "task_reported": 0.0, "task_est": 0.0,
                                        "task_nocost": 0, "passed": set()})
            c["runs"] += 1
            tokens = {k: _num(ev.get(k)) for k in ("tokens_in", "tokens_out", "tokens_cached")}
            tokens = {k: v for k, v in tokens.items() if v is not None}
            cost = _num(ev.get("cost_usd"))
            if "tokens_in" in tokens or "tokens_out" in tokens:
                c["tok_runs"] += 1
                c["tin"] += tokens.get("tokens_in", 0)
                c["tout"] += tokens.get("tokens_out", 0)
            reported, est = 0.0, 0.0
            if cost is not None:
                c["costed"] += 1
                c["reported"] += cost
                reported = cost
            else:
                guess = estimate(prices, lane, tokens)
                if guess is not None:
                    c["estimated"] += guess
                    c["est_runs"] += 1
                    est = guess
            if task:
                c["task_reported"] += reported
                c["task_est"] += est
                if cost is None:
                    c["task_nocost"] += 1
                last_lane[task] = lane
        elif ev.get("kind") == "check" and ev.get("status") == "pass" and task in last_lane:
            lanes[last_lane[task]]["passed"].add(task)
    return lanes


def _usd(x):
    return "$%.4f" % x if x < 1 else "$%.2f" % x


def report(events, prices_path=""):
    prices, bad = read_prices(prices_path)
    lanes = tally(events, prices)
    if not lanes:
        return ["no runs in the log"]
    out = ["%-44s %5s %6s %10s %10s %9s %9s %6s %11s %11s" % (
        "LANE", "RUNS", "COSTED", "REPORTED", "~ESTIMATED", "TOK IN", "TOK OUT", "PASSED", "$/PASSED", "~$/PASSED")]
    for lane, c in lanes.items():
        n = len(c["passed"])
        rep = _usd(c["reported"]) if c["costed"] else "-"
        est = "~" + _usd(c["estimated"]) if c["est_runs"] else "-"
        tin = str(c["tin"]) if c["tok_runs"] else "-"
        tout = str(c["tout"]) if c["tok_runs"] else "-"
        per = _usd(c["task_reported"] / n) if n and c["costed"] else "-"
        # Reported plus estimated per passed task, marked so it cannot pass for a reported number.
        per_est = "~" + _usd((c["task_reported"] + c["task_est"]) / n) if n and c["est_runs"] else "-"
        out.append("%-44s %5d %6d %10s %10s %9s %9s %6d %11s %11s" % (
            lane, c["runs"], c["costed"], rep, est, tin, tout, n, per, per_est))
    out.append("")
    out.append("COSTED = runs whose tool reported a cost; the others are not free, they are not counted in REPORTED.")
    for lane, c in lanes.items():
        if c["runs"] != c["costed"]:
            out.append("%s: %d runs, %d with reported cost" % (lane, c["runs"], c["costed"]))
    if any(c["est_runs"] for c in lanes.values()):
        out.append("~ = computed from your price file for runs that had tokens but no reported cost: an estimate, "
                   "never added to REPORTED. ~$/PASSED is reported plus estimated.")
    if any(c["task_nocost"] and c["costed"] for c in lanes.values()):
        out.append("$/PASSED covers only the runs with a reported cost, so a lane with uncosted runs looks cheaper than it was.")
    if bad:
        out.append("price file: %d line(s) ignored (expected: pattern, input per million, output per million, "
                   "optional cached per million)" % bad)
    return out


if __name__ == "__main__":
    print(__doc__)
    sys.exit(2)
