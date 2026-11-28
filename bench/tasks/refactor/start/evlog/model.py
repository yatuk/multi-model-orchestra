"""Events and the line format.

A log line is `TIMESTAMP LEVEL MESSAGE`, separated by single spaces:
    2026-03-01T10:15:00 WARN disk almost full
TIMESTAMP is exactly YYYY-MM-DDTHH:MM:SS. LEVEL is one of LEVELS. MESSAGE is the rest of
the line with surrounding spaces removed; it may be empty.
"""
import re
from dataclasses import dataclass
from datetime import datetime, timedelta

LEVELS = ("DEBUG", "INFO", "WARN", "ERROR")
RANK = {name: i for i, name in enumerate(LEVELS)}

_LINE = re.compile(r"(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2}) ([A-Z]+)(?: (.*))?")


class ParseError(ValueError):
    """A malformed line in strict mode. The message starts with "line N: "."""


@dataclass(frozen=True)
class Event:
    time: datetime      # UTC, naive
    level: str
    message: str
    line: int           # 1-based position of the line in the input, blank lines included


def parse_line(text, number, utc_offset):
    """Return an Event for one line, or a reason string when the line is malformed."""
    m = _LINE.fullmatch(text)
    if not m:
        return "not TIMESTAMP LEVEL MESSAGE"
    level = m.group(7)
    if level not in RANK:
        return f"unknown level {level}"
    try:
        written = datetime(*(int(g) for g in m.group(1, 2, 3, 4, 5, 6)))
    except ValueError:
        return "bad timestamp"
    return Event(written - timedelta(minutes=utc_offset), level, (m.group(8) or "").strip(), number)
