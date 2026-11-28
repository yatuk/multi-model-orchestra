"""How values are written to and read from the database.

Timestamps are stored as text, 'YYYY-MM-DD HH:MM', so that SQL can compare and sort them
as plain strings. Reading is lenient (any ISO form), writing is not.
"""
from datetime import date, datetime

DB_FORMAT = "%Y-%m-%d %H:%M"


def to_db(dt):
    return dt.strftime(DB_FORMAT)


def canonical(text):
    """Any ISO form of a stored timestamp, rewritten as DB_FORMAT."""
    return to_db(from_db(text)) if text else text


def from_db(text):
    if text is None:
        return None
    return datetime.fromisoformat(text)


def day_start(d):
    """The first stored value of day d, for range queries."""
    return f"{d.isoformat()} 00:00"


def day_key(d):
    if isinstance(d, datetime):
        d = d.date()
    if isinstance(d, date):
        return d.isoformat()
    return str(d)[:10]
