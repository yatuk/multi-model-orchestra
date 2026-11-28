"""Summaries over a log, in one pass."""
from collections import Counter

from .model import LEVELS
from .reader import parse_events, resolve


def summarize(lines, options=None):
    """Return {"total", "by_level", "first", "last"} for the events in `lines`.

    by_level has every level in LEVELS, zero when absent. first and last are the earliest
    and latest event time as ISO text ("2026-03-01T10:15:00"), or None when there are no
    events. Reads `lines` once and keeps no list of events.
    """
    opts = resolve(options)
    by_level = {name: 0 for name in LEVELS}
    total, first, last = 0, None, None
    for e in parse_events(lines, opts):
        total += 1
        by_level[e.level] += 1
        if first is None or e.time < first:
            first = e.time
        if last is None or e.time > last:
            last = e.time
    return {
        "total": total,
        "by_level": by_level,
        "first": first.isoformat() if first is not None else None,
        "last": last.isoformat() if last is not None else None,
    }


def top_messages(lines, n=3, options=None):
    """Return the n most frequent messages as [(message, count), ...].

    Higher count first; equal counts keep the order in which each message first appeared.
    """
    opts = resolve(options)
    counts = Counter(e.message for e in parse_events(lines, opts))
    ranked = sorted(counts.items(), key=lambda kv: -kv[1])
    return ranked[:n]
