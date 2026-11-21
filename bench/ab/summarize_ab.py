"""Print a markdown table from the per-run JSON records in a results directory."""
import json
import sys
from pathlib import Path


def tokens(rec):
    t = {"in": 0, "out": 0, "cache_read": 0, "cache_write": 0}
    for m in (rec.get("modelUsage") or {}).values():
        t["in"] += m.get("inputTokens", 0)
        t["out"] += m.get("outputTokens", 0)
        t["cache_read"] += m.get("cacheReadInputTokens", 0)
        t["cache_write"] += m.get("cacheCreationInputTokens", 0)
    return t


def models(rec):
    parts = []
    for name, m in (rec.get("modelUsage") or {}).items():
        parts.append(f"{name.replace('claude-', '')} ${m.get('costUSD', 0):.2f}")
    return ", ".join(parts)


def main():
    out = Path(sys.argv[1])
    recs = sorted((json.loads(p.read_text(encoding="utf-8")) for p in out.glob("[AB]*.json")),
                  key=lambda r: (r["arm"], r["run"]))
    print("| Run | Cost (USD) | Tokens in+out (cache read / write) | Wall (min) | Turns | Hidden tests | Per task (bug/feat/refac/parse) | Visible tests intact | Cost by model |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in recs:
        t, g = tokens(r), r["grade"]
        per = " / ".join(v for v in g["tasks"].values())
        cost = r.get("total_cost_usd")
        wall = (r.get("wall_s") or 0) / 60
        print(f"| {r['arm']}{r['run']} | {cost if cost is None else f'{cost:.2f}'} | {t['in'] + t['out']:,} ({t['cache_read']:,} / {t['cache_write']:,}) "
              f"| {wall:.1f} | {r.get('num_turns')} | {g['hidden_total']} | {per} | {'yes' if g['visible_tests_intact'] else 'NO'} | {models(r)} |")


if __name__ == "__main__":
    main()
