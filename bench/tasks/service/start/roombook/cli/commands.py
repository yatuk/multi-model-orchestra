"""Handlers for the everyday commands. Each takes (args, app) and returns an exit code."""
from ..parse.query import day_range
from ..report import listing
from ..sched.slots import free_windows
from ..util.ids import parse_id
from ..util.timefmt import fmt_hm, parse_day, parse_duration, parse_when
from .. import clock
from ..model.room import norm_code
from ..errors import NotFound


def cmd_book(args, app):
    start = parse_when(args.start)
    minutes = parse_duration(args.duration)
    b, warns = app.service.book(args.room, start, minutes, title=args.title or "",
                                attendees=args.people, owner=args.for_)
    app.out.line(f"booked {b.label}: {b.room} {b.span_text()}")
    for w in warns:
        app.out.warn(w.message)
    return 0


def cmd_cancel(args, app):
    b, late = app.service.cancel(parse_id(args.id))
    app.out.line(f"cancelled {b.label} ({b.room} {b.span_text()})")
    if late:
        app.out.note(f"late cancellation (less than {app.settings.late_cancel_hours} hours before the start)")
    return 0


def cmd_move(args, app):
    minutes = parse_duration(args.length) if args.length else None
    b, warns = app.service.move(parse_id(args.id), parse_when(args.start), minutes)
    app.out.line(f"moved {b.label} to {b.span_text()}")
    for w in warns:
        app.out.warn(w.message)
    return 0


def cmd_show(args, app):
    b = app.service.show(parse_id(args.id))
    app.out.lines(listing.show_lines(b, app.service.rooms.get(b.room)))
    return 0


def cmd_list(args, app):
    first, stop = day_range(args.day, args.week, args.first, args.last)
    room = norm_code(args.room) if args.room else None
    bookings = app.service.bookings.between(first, stop, room)
    if args.format == "tsv":
        app.out.lines(listing.tsv_lines(bookings))
    else:
        app.out.lines(listing.text_lines(bookings, first, stop))
    return 0


def cmd_mine(args, app):
    items = app.service.upcoming_for(args.owner or app.actor)
    if not items:
        app.out.line("no upcoming bookings")
        return 0
    for b in items[: args.limit]:
        app.out.line(f"{b.label}  {b.room:<6} {b.span_text()}  {b.title}".rstrip())
    return 0


def cmd_free(args, app):
    room = norm_code(args.room)
    if app.service.rooms.get(room) is None:
        raise NotFound(f"there is no room {room}")
    day = parse_day(args.day)
    length = parse_duration(args.length)
    windows = free_windows(app.service.bookings.on_day(day, room), day, app.settings, length, now=clock.now())
    if not windows:
        app.out.line(f"{room} has no free {length} minutes on {day.isoformat()}")
        return 0
    for start, end in windows:
        app.out.line(f"{fmt_hm(start)}-{fmt_hm(end)}")
    return 0


def cmd_series(args, app):
    start = parse_when(args.start)
    minutes = parse_duration(args.duration)
    made, skipped = app.service.series(args.room, start, minutes, args.weeks, title=args.title or "",
                                       attendees=args.people)
    app.out.line(f"series {made[0].series_id}: {len(made)} bookings created ({made[0].label} to {made[-1].label})")
    for b, errs in skipped:
        app.out.line(f"skipped {b.start:%Y-%m-%d %H:%M}: {'; '.join(e.message for e in errs)}")
    return 0
