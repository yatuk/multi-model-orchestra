"""Turning lines into events."""
from dataclasses import dataclass

from .model import RANK, ParseError, parse_line


@dataclass(frozen=True)
class ParseOptions:
    """How to parse.

    min_level   events below this level are dropped (DEBUG < INFO < WARN < ERROR).
    strict      when True, the first malformed line raises ParseError("line N: reason");
                when False, malformed lines are skipped. A line is malformed whatever its
                level, so a malformed line raises even when its level is below min_level.
    utc_offset  minutes east of UTC that the timestamps are written in; Event.time is
                the written time minus the offset (written 12:00 at +90 is 10:30 UTC).
    """
    min_level: str = "DEBUG"
    strict: bool = False
    utc_offset: int = 0

    def __post_init__(self):
        if self.min_level not in RANK:
            raise ValueError(f"unknown level {self.min_level!r}")


def resolve(options):
    """Check `options` at call time, so a caller still using the old flags fails at once."""
    if options is None:
        return ParseOptions()
    if not isinstance(options, ParseOptions):
        raise TypeError(f"options must be a ParseOptions or None, got {type(options).__name__}")
    return options


def parse_events(lines, options=None):
    """Return an iterator of Event over `lines`, in input order, reading one line at a time.

    lines is any iterable of strings (a list, a generator, an open file); a trailing
    "\\n" or "\\r\\n" on a line is ignored. Blank lines (empty or only spaces) are skipped
    and are never malformed, but they count for line numbers. In strict mode the
    ParseError comes when iteration reaches the malformed line.
    """
    return _events(lines, resolve(options))


def _events(lines, opts):
    floor = RANK[opts.min_level]
    for number, raw in enumerate(lines, 1):
        text = raw.rstrip("\r\n")
        if not text.strip():
            continue
        result = parse_line(text, number, opts.utc_offset)
        if isinstance(result, str):
            if opts.strict:
                raise ParseError(f"line {number}: {result}")
            continue
        if RANK[result.level] >= floor:
            yield result
