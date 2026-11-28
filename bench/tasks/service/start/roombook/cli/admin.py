"""Handlers for rooms, import, backups and reports."""
from datetime import datetime

from ..errors import PermissionDenied, UsageError
from ..model.room import Room, features_from_text, norm_code
from ..parse.query import day_range
from ..parse.roomfile import read_rooms
from ..report import export, usage
from ..store import backup
from ..util.text import render_table
from ..util.timefmt import fmt_hm, month_bounds, parse_when


def _admin_only(app, what):
    if not app.settings.is_admin(app.actor):
        raise PermissionDenied(f"only an admin may {what}")


def cmd_rooms(args, app):
    store = app.service.rooms
    if args.rooms_cmd == "list":
        rows = [(r.code, r.name, r.capacity, ",".join(r.features)) for r in store.all()]
        if not rows:
            app.out.line("no rooms yet")
            return 0
        app.out.lines(render_table(("code", "name", "capacity", "features"), rows, right=(2,)))
        return 0
    _admin_only(app, "change rooms")
    if args.rooms_cmd == "add":
        if args.capacity < 1:
            raise UsageError("capacity must be at least 1")
        store.save(Room(code=norm_code(args.code), name=args.name or "", capacity=args.capacity,
                        features=features_from_text(args.features)))
        app.out.line(f"room {norm_code(args.code)} saved")
        return 0
    if args.rooms_cmd == "load":
        rooms = read_rooms(args.file)
        for r in rooms:
            store.save(r)
        app.out.line(f"{len(rooms)} rooms loaded")
        return 0
    raise UsageError("rooms: use list, add or load")


def cmd_import(args, app):
    s = app.service.import_file(args.file)
    app.out.line(f"imported {s.imported}, skipped {len(s.skipped) + len(s.problems)}")
    for line, msg in sorted(s.problems + s.skipped, key=lambda p: p[0] or 0):
        app.out.line(f"  line {line}: {msg}")
    return 0


def cmd_backup(args, app):
    n = backup.dump(app.conn, args.file)
    app.out.line(f"{n} bookings written to {args.file}")
    return 0


def cmd_restore(args, app):
    _admin_only(app, "restore a backup")
    rooms, bookings = backup.restore(app.conn, args.file, replace=args.replace)
    app.out.line(f"restored {rooms} rooms and {bookings} bookings")
    return 0


def cmd_usage(args, app):
    first, stop = month_bounds(args.month)
    bookings = app.service.bookings.between(first, stop)
    rows = usage.monthly(bookings, app.service.rooms.codes(), first, stop, app.settings)
    if args.format == "tsv":
        app.out.lines(usage.tsv_lines(rows))
    else:
        app.out.lines(usage.text_lines(rows, f"Room usage {args.month}"))
    return 0


def cmd_export(args, app):
    first, stop = day_range(args.day, args.week, args.first, args.last)
    text = export.finance_csv(app.service.bookings.between(first, stop))
    if args.out:
        with open(args.out, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        app.out.line(f"written to {args.out}")
    else:
        app.out.stdout.write(text)
    return 0


def cmd_status(args, app):
    when = parse_when(args.at) if args.at else None
    for st in app.service.status(when):
        if st.current:
            c = st.current
            app.out.line(f"{st.room.code:<6} busy until {fmt_hm(c.end)} ({c.label} {c.title})".rstrip())
        elif st.upcoming:
            app.out.line(f"{st.room.code:<6} free until {fmt_hm(st.upcoming.start)}")
        else:
            app.out.line(f"{st.room.code:<6} free")
    return 0
