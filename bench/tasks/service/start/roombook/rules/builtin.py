"""The booking rules every building uses. Limits come from settings, never from here."""
from datetime import timedelta

from ..util.timefmt import fmt_hm
from .base import error, rule, warning

# The old kiosk refused cancellations less than 48 hours ahead. Nothing reads this any more;
# kept so the kiosk export script, which imports it, keeps working.
LEGACY_NOTICE_HOURS = 48


@rule("room")
def room_exists(b, ctx):
    if b.room not in ctx.rooms:
        return [error("room", f"there is no room {b.room}")]
    return []


@rule("past")
def not_in_past(b, ctx):
    if b.start < ctx.now:
        return [error("past", "the start time has already passed")]
    return []


@rule("advance")
def within_advance(b, ctx):
    limit = ctx.now + timedelta(days=ctx.settings.advance_days)
    if b.start > limit:
        return [error("advance", f"bookings open at most {ctx.settings.advance_days} days ahead")]
    return []


@rule("hours")
def opening_hours(b, ctx):
    s = ctx.settings
    if b.end.date() != b.start.date():
        return [error("hours", "a booking must end on the day it starts")]
    if b.start.hour < s.open_hour or (b.end.hour, b.end.minute) > (s.close_hour, 0):
        return [error("hours", f"the building is open {s.open_hour:02d}:00-{s.close_hour:02d}:00")]
    return []


@rule("length")
def max_duration(b, ctx):
    if b.minutes > ctx.settings.max_booking_minutes:
        return [error("length", f"a booking may last at most {ctx.settings.max_booking_minutes} minutes")]
    return []


@rule("capacity")
def capacity(b, ctx):
    room = ctx.rooms.get(b.room)
    if room and b.attendees > room.capacity:
        return [error("capacity", f"room {room.code} holds {room.capacity}, not {b.attendees}")]
    return []


@rule("conflict")
def no_conflict(b, ctx):
    found = []
    for other in ctx.bookings.overlapping(b.room, b.start, b.end, exclude_id=b.id):
        found.append(error("conflict", f"overlaps {other.label} ({fmt_hm(other.start)}-{fmt_hm(other.end)}, "
                                       f"{other.owner})"))
    return found


@rule("weekend", kinds=("book", "move"))
def weekend(b, ctx):
    if ctx.settings.weekend_warning and b.start.weekday() >= 5:
        return [warning("weekend", "that is a weekend; the building may be locked")]
    return []
