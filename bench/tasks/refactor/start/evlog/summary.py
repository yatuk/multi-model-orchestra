"""Summaries over a log."""
from collections import Counter

from .model import LEVELS
from .reader import parse_events


def summarize(lines, min_level="DEBUG", strict=False, utc_offset=0):
    """Return {"total", "by_level", "first", "last"} for the events in `lines`.

    by_level has every level in LEVELS, zero when absent. first and last are the earliest
    and latest event time as ISO text ("2026-03-01T10:15:00"), or None when there are no
    events. The parse arguments mean what they mean for parse_events.
    """
    events = parse_events(lines, min_level, strict, utc_offset)
    by_level = {name: 0 for name in LEVELS}
    for e in events:
        by_level[e.level] += 1
    return {
        "total": len(events),
        "by_level": by_level,
        "first": min(e.time for e in events).isoformat() if events else None,
        "last": max(e.time for e in events).isoformat() if events else None,
    }


def top_messages(lines, n=3, min_level="DEBUG", strict=False, utc_offset=0):
    """Return the n most frequent messages as [(message, count), ...].

    Higher count first; equal counts keep the order in which each message first appeared.
    """
    counts = Counter(e.message for e in parse_events(lines, min_level, strict, utc_offset))
    ranked = sorted(counts.items(), key=lambda kv: -kv[1])
    return ranked[:n]
