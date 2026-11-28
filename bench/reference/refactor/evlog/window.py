"""Time windows and tails over a log."""
from collections import deque

from .reader import parse_events, resolve


def in_window(lines, start, end, options=None):
    """Return an iterator of the events with start <= time < end (UTC, naive), in input order.

    The window is half open: an event exactly at `end` is outside. Lazy like parse_events.
    """
    events = parse_events(lines, resolve(options))
    return (e for e in events if start <= e.time < end)


def tail(lines, n=10, options=None):
    """Return the last n events, in input order, as a list.

    n must be 0 or more; a negative n raises ValueError before any line is read.
    Holds at most n events while reading.
    """
    opts = resolve(options)
    if n < 0:
        raise ValueError(f"n must be 0 or more, got {n}")
    return list(deque(parse_events(lines, opts), maxlen=n))
