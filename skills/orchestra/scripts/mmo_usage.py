"""What a lane's own tool reported about the run: tokens, cost, served model. Stdlib only.

    python mmo_usage.py PROVIDER RAW_FILE REQUESTED_MODEL [API_SIDE_FILE]

Prints three lines for mmo-run (each may be empty):
    1. header fields, one leading space each:  " in=1200 out=80 cached=900 cost=0.0123 served=x"
    2. MMO_LOG fragment, JSON members with a leading comma:  ,"tokens_in":1200,"cost_usd":0.0123
    3. "cost" when the tool says it stopped at the cost ceiling (--max-cost), else empty

Nothing is estimated: a field the output does not contain is left out. Only shapes this repo has
confirmed are read:
    claude lanes   claude -p --output-format json: total_cost_usd, usage (input_tokens, output_tokens,
                   cache_read_input_tokens), modelUsage keys for the served model, and the result
                   subtype error_max_budget_usd for the ceiling. claude-deepseek, claude-kimi and
                   claude-minimax run the same CLI, so they carry the same fields.
    api lane       mmo_api.py writes the response's usage object and model to a side file.
Every other lane prints no usage this repo has seen (see docs/cost.md); they get no fields.
"""
import json
import math
import os
import sys

CLAUDE_LANES = {"claude", "claude-deepseek", "claude-kimi", "claude-minimax"}


def _num(value, integer=False):
    """A reported number, or None. Booleans, negatives, NaN and text are not numbers."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if value < 0 or (isinstance(value, float) and not math.isfinite(value)):
        return None
    if integer:
        return int(value) if float(value).is_integer() else None
    return value


def _norm(model):
    return (model or "").strip().lower()


def _same_model(requested, served):
    """Aliases (sonnet) and dated ids (claude-sonnet-4-6) count as the same model."""
    a, b = _norm(requested), _norm(served)
    return not a or not b or a == b or a in b or b in a


def _claude(raw, requested):
    try:
        data = json.loads(raw)
    except ValueError:
        return {}
    if isinstance(data, list):  # some versions emit the event list; the result is last
        data = data[-1] if data else {}
    if not isinstance(data, dict):
        return {}
    out = {}
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    for key, field in (("input_tokens", "tokens_in"), ("output_tokens", "tokens_out"),
                       ("cache_read_input_tokens", "tokens_cached")):
        n = _num(usage.get(key), integer=True)
        if n is not None:
            out[field] = n
    cost = _num(data.get("total_cost_usd"))
    if cost is not None:
        out["cost_usd"] = cost
    models = data.get("modelUsage")
    if isinstance(models, dict) and models:
        keys = [k for k in models if isinstance(k, str)]
        match = [k for k in keys if _same_model(requested, k)] if requested else []
        if match:
            out["served_model"] = match[0]
        elif keys:  # none looks like the requested one: report the one that wrote the most
            def written(k):
                v = models[k] if isinstance(models[k], dict) else {}
                return _num(v.get("outputTokens")) or 0
            out["served_model"] = max(keys, key=written)
    if data.get("subtype") == "error_max_budget_usd":
        out["ceiling"] = "cost"
    return out


def _api(side_file):
    try:
        with open(side_file, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError, TypeError):
        return {}
    if not isinstance(data, dict):
        return {}
    out = {}
    usage = data.get("usage") if isinstance(data.get("usage"), dict) else {}
    for key, field in (("prompt_tokens", "tokens_in"), ("completion_tokens", "tokens_out")):
        n = _num(usage.get(key), integer=True)
        if n is not None:
            out[field] = n
    cost = _num(usage.get("cost"))
    if cost is not None:
        out["cost_usd"] = cost
    if isinstance(data.get("model"), str) and data["model"].strip():
        out["served_model"] = data["model"].strip()
    return out


def usage_of(provider, raw, requested="", api_file=""):
    """Dict of what was reported (tokens_in, tokens_out, tokens_cached, cost_usd, served_model, ceiling)."""
    if provider in CLAUDE_LANES:
        return _claude(raw, requested)
    if provider == "api" and api_file:
        return _api(api_file)
    return {}


def _money(x):
    s = ("%.6f" % x).rstrip("0").rstrip(".")
    return s or "0"


def header_fields(u, requested=""):
    parts = []
    for key, name in (("tokens_in", "in"), ("tokens_out", "out"), ("tokens_cached", "cached")):
        if key in u:
            parts.append("%s=%d" % (name, u[key]))
    if "cost_usd" in u:
        parts.append("cost=" + _money(u["cost_usd"]))
    served = u.get("served_model")
    if served and not _same_model(requested.split(":", 1)[-1] if ":" in requested else requested, served):
        parts.append("served=" + "".join(served.split()))
    return "".join(" " + p for p in parts)


def log_fragment(u):
    parts = []
    for key in ("tokens_in", "tokens_out", "tokens_cached", "cost_usd", "served_model"):
        if key in u:
            parts.append('"%s":%s' % (key, json.dumps(u[key] if key != "cost_usd" else float(u[key]))))
    return "".join("," + p for p in parts)


def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    provider, raw_path, requested = argv[0], argv[1], argv[2]
    api_file = argv[3] if len(argv) > 3 else ""
    try:
        with open(raw_path, encoding="utf-8", errors="replace") as f:
            raw = f.read()
    except OSError:
        raw = ""
    u = usage_of(provider, raw, requested, api_file)
    # Bytes, so a Windows console does not turn the newlines into CRLF and leak a CR into the header.
    text = "%s\n%s\n%s\n" % (header_fields(u, requested), log_fragment(u), u.get("ceiling", ""))
    sys.stdout.buffer.write(text.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
