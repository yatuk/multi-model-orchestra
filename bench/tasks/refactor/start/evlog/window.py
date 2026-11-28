"""Time windows over a log."""
from .reader import parse_events


def in_window(lines, start, end, min_level="DEBUG", strict=False, utc_offset=0):
    """Return the events with start <= time < end (UTC, naive datetimes), in input order.

    The window is half open: an event exactly at `end` is outside. The parse arguments
    mean what they mean for parse_events.
    """
    return [e for e in parse_events(lines, min_level, strict, utc_offset) if start <= e.time < end]


def tail(lines, n=10, min_level="DEBUG", strict=False, utc_offset=0):
    """Return the last n events, in input order, as a list.

    n must be 0 or more; a negative n raises ValueError before any line is read.
    The parse arguments mean what they mean for parse_events.
    """
    if n < 0:
        raise ValueError(f"n must be 0 or more, got {n}")
    events = parse_events(lines, min_level, strict, utc_offset)
    return events[max(0, len(events) - n):] if n else []
