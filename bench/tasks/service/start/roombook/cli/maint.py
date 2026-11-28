"""Handlers for the housekeeping commands: log, doctor, purge, calendar, digest."""
from itertools import combinations

from ..errors import NotFound, PermissionDenied
from ..model.room import norm_code
from ..parse.query import day_range
from ..report.digest import digest_lines
from ..report.ics import feed
from ..store.audit import AuditLog
from ..util.ids import format_id, parse_id
from ..util.timefmt import parse_day


def cmd_log(args, app):
    booking_id = parse_id(args.id) if args.id else None
    entries = AuditLog(app.conn).recent(args.limit, booking_id)
    if not entries:
        app.out.line("nothing logged")
        return 0
    for e in entries:
        ref = format_id(e.booking_id) if e.booking_id else "-"
        app.out.line(f"{e.at:%Y-%m-%d %H:%M}  {e.actor:<10} {e.action:<8} {ref:<6} {e.detail}".rstrip())
    return 0


def find_problems(bookings, rooms, settings):
    """Double bookings and bookings outside opening hours. Compared in Python, not SQL,
    so the check does not depend on how the rows were written."""
    problems = []
    by_room = {}
    for b in bookings:
        by_room.setdefault(b.room, []).append(b)
    for code, items in sorted(by_room.items()):
        if code not in rooms:
            problems.append(f"{code}: room no longer exists ({len(items)} bookings)")
        items.sort(key=lambda b: b.start)
        for a, b in combinations(items, 2):
            if a.overlaps(b.start, b.end):
                problems.append(f"{code}: {a.label} and {b.label} overlap on {a.start:%Y-%m-%d}")
        for b in items:
            if b.start.hour < settings.open_hour or (b.end.hour, b.end.minute) > (settings.close_hour, 0):
                problems.append(f"{code}: {b.label} is outside opening hours")
    return problems


def cmd_doctor(args, app):
    problems = find_problems(app.service.bookings.all(), app.service.rooms.by_code(), app.settings)
    if not problems:
        app.out.line("no problems found")
        return 0
    app.out.lines(problems)
    return 1


def cmd_purge(args, app):
    if not app.settings.is_admin(app.actor):
        raise PermissionDenied("only an admin may purge")
    n = app.service.purge(parse_day(args.before))
    app.out.line(f"purged {n} bookings that ended before {args.before}")
    return 0


def cmd_calendar(args, app):
    room = app.service.rooms.get(norm_code(args.room))
    if room is None:
        raise NotFound(f"there is no room {norm_code(args.room)}")
    first, stop = day_range(args.day, args.week, args.first, args.last)
    text = feed(app.service.bookings.between(first, stop, room.code), room)
    app.out.stdout.write(text)
    return 0


def cmd_digest(args, app):
    day = parse_day(args.day)
    bookings = app.service.bookings.on_day(day)
    app.out.lines(digest_lines(bookings, app.service.rooms.all(), day, app.settings))
    return 0
