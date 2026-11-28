"""Parsing and formatting of the times people type and read.

Accepted start times (parse_when):
    2030-01-07 09:00    2030-01-07T09:00    today 09:00    tomorrow 9:30    09:00 (today)
Accepted durations (parse_duration):
    90m   90   1h   1h30   1h30m   1.5h   1:30
Accepted days (parse_day):
    today   tomorrow   yesterday   2030-01-07   mon .. sun (the next one, today included)

DISPLAY_FORMAT is what people see. It is not the storage format; the store has its own.
"""
import re
from datetime import date, datetime, timedelta

from .. import clock
from ..errors import UsageError

DISPLAY_FORMAT = "%Y-%m-%d %H:%M"
DAY_FORMAT = "%Y-%m-%d"
WEEKDAYS = ("mon", "tue", "wed", "thu", "fri", "sat", "sun")

_TIME = re.compile(r"^(\d{1,2})[:.](\d{2})$")
_DUR_HM = re.compile(r"^(?:(\d+)h)?(?:(\d+)m?)?$")
_ISO_T = re.compile(r"^\d{4}-\d{2}-\d{2}T")


def parse_time_of_day(text):
    m = _TIME.match(text.strip())
    if not m:
        raise UsageError(f"not a time of day: {text!r} (use HH:MM)")
    h, mi = int(m.group(1)), int(m.group(2))
    if h > 23 or mi > 59:
        raise UsageError(f"not a time of day: {text!r}")
    return h, mi


def parse_day(text, today=None):
    today = today or clock.today()
    t = text.strip().lower()
    if t == "today":
        return today
    if t == "tomorrow":
        return today + timedelta(days=1)
    if t == "yesterday":
        return today - timedelta(days=1)
    if t[:3] in WEEKDAYS and len(t) <= 9:
        want = WEEKDAYS.index(t[:3])
        return today + timedelta(days=(want - today.weekday()) % 7)
    try:
        return datetime.strptime(t, DAY_FORMAT).date()
    except ValueError:
        raise UsageError(f"not a day: {text!r} (use YYYY-MM-DD, today, tomorrow or a weekday)") from None


def parse_when(text, today=None):
    """A start time. A bare time means today."""
    t = text.strip()
    if _ISO_T.match(t):
        t = t[:10] + " " + t[11:]
    parts = t.split()
    if len(parts) == 1:
        if ":" in parts[0] or "." in parts[0]:
            day, tod = (today or clock.today()), parts[0]
        else:
            raise UsageError(f"not a start time: {text!r}")
    elif len(parts) == 2:
        day, tod = parse_day(parts[0], today), parts[1]
    else:
        raise UsageError(f"not a start time: {text!r}")
    h, mi = parse_time_of_day(tod)
    return datetime(day.year, day.month, day.day, h, mi)


def parse_duration(text):
    """Minutes as an int. A bare number is minutes."""
    t = text.strip().lower().replace(" ", "")
    if not t:
        raise UsageError("empty duration")
    if ":" in t:
        h, _, m = t.partition(":")
        if h.isdigit() and m.isdigit():
            return int(h) * 60 + int(m)
        raise UsageError(f"not a duration: {text!r}")
    if t.endswith("h") and re.fullmatch(r"\d+\.\d+h", t):
        return round(float(t[:-1]) * 60)
    m = _DUR_HM.match(t)
    if not m or not (m.group(1) or m.group(2)):
        raise UsageError(f"not a duration: {text!r} (try 90m, 1h30 or 1.5h)")
    minutes = int(m.group(1) or 0) * 60 + int(m.group(2) or 0)
    if minutes <= 0:
        raise UsageError("a duration must be more than zero minutes")
    return minutes


def fmt_hm(dt):
    return dt.strftime("%H:%M")


def fmt_day(d):
    """'Mon 2030-01-07'."""
    return d.strftime("%a %Y-%m-%d")


def fmt_span(start, end):
    if start.date() == end.date():
        return f"{start.strftime(DISPLAY_FORMAT)}-{fmt_hm(end)}"
    return f"{start.strftime(DISPLAY_FORMAT)} - {end.strftime(DISPLAY_FORMAT)}"


def fmt_minutes(minutes):
    h, m = divmod(int(minutes), 60)
    if h and m:
        return f"{h}h{m:02d}"
    if h:
        return f"{h}h"
    return f"{m}m"


def week_of(d):
    """Monday and the next Monday around day d."""
    monday = d - timedelta(days=d.weekday())
    return monday, monday + timedelta(days=7)


def month_bounds(text):
    """'2030-01' -> (date(2030,1,1), date(2030,2,1))."""
    try:
        y, m = (int(x) for x in text.split("-"))
        first = date(y, m, 1)
    except ValueError:
        raise UsageError(f"not a month: {text!r} (use YYYY-MM)") from None
    nxt = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
    return first, nxt


def days(first, stop):
    d = first
    while d < stop:
        yield d
        d += timedelta(days=1)


def at(d, hour, minute=0):
    return datetime(d.year, d.month, d.day, hour, minute)
