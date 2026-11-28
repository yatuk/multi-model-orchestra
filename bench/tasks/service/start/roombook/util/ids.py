"""Booking ids as people see them: B0007. The database keeps the plain integer."""
import re

from ..errors import UsageError

_ID = re.compile(r"^[Bb]?0*(\d+)$")


def format_id(n):
    return f"B{int(n):04d}"


def parse_id(text):
    m = _ID.match(str(text).strip())
    if not m:
        raise UsageError(f"not a booking id: {text!r} (looks like B0007)")
    return int(m.group(1))
