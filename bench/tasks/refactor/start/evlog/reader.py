"""Turning lines into events."""
from .model import RANK, ParseError, parse_line


def parse_events(lines, min_level="DEBUG", strict=False, utc_offset=0):
    """Parse log lines and return a list of Event, in input order.

    lines       the input lines; a trailing "\\n" or "\\r\\n" on a line is ignored.
    min_level   events below this level are dropped (DEBUG < INFO < WARN < ERROR).
    strict      when True, the first malformed line raises ParseError("line N: reason");
                when False, malformed lines are skipped. A line is malformed whatever its
                level, so a malformed line raises even when its level is below min_level.
    utc_offset  minutes east of UTC that the timestamps are written in; Event.time is
                the written time minus the offset (written 12:00 at +90 is 10:30 UTC).
    Blank lines (empty or only spaces) are skipped and are never malformed, but they
    count for line numbers.
    """
    if min_level not in RANK:
        raise ValueError(f"unknown level {min_level!r}")
    floor = RANK[min_level]
    events = []
    for number, raw in enumerate(lines, 1):
        text = raw.rstrip("\r\n")
        if not text.strip():
            continue
        result = parse_line(text, number, utc_offset)
        if isinstance(result, str):
            if strict:
                raise ParseError(f"line {number}: {result}")
            continue
        if RANK[result.level] >= floor:
            events.append(result)
    return events
