"""Free time in a room on one day.

A free window starts on a step boundary (slot_step_minutes, counted from midnight), lies
inside opening hours, does not touch the past when the day is today, and is at least as
long as asked. Windows are as long as possible: 09:00-12:00, not 09:00-10:00, 10:00-11:00...
"""
from datetime import timedelta

from ..util.timefmt import at


def _round_up(dt, step):
    minutes = dt.hour * 60 + dt.minute
    rest = minutes % step
    if rest == 0:
        return dt
    return dt + timedelta(minutes=step - rest)


def free_windows(day_bookings, day, settings, length, now=None):
    """day_bookings: the room's bookings on that day (any order). Returns [(start, end)]."""
    step = settings.slot_step_minutes
    opens, closes = at(day, settings.open_hour), at(day, settings.close_hour)
    cursor = opens
    if now is not None and now.date() == day and now > cursor:
        cursor = _round_up(now, step)
    windows = []
    for b in sorted(day_bookings, key=lambda b: b.start):
        if b.end <= cursor:
            continue
        if b.start > cursor:
            _add(windows, cursor, min(b.start, closes), length)
        cursor = max(cursor, _round_up(b.end, step))
        if cursor >= closes:
            break
    if cursor < closes:
        _add(windows, cursor, closes, length)
    return windows


def _add(windows, start, end, length):
    if (end - start) >= timedelta(minutes=length):
        windows.append((start, end))


def first_fit(day_bookings, day, settings, length, now=None):
    for start, _end in free_windows(day_bookings, day, settings, length, now):
        return start
    return None
