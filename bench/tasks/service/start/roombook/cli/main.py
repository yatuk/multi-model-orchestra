"""Command line: python -m roombook [--db FILE] [--config FILE] [--user NAME] COMMAND ...

The user defaults to $ROOMBOOK_USER, then the login name. The database defaults to the
db_path setting.
"""
import argparse
import getpass
import os

from .. import settings as settings_mod
from ..errors import Refused, RoombookError
from ..service import BookingService
from ..store.db import open_db
from . import admin, commands, maint
from .output import Out


class App:
    """What a handler needs: the service, the settings, the output, the open connection."""

    def __init__(self, conn, settings, actor, out):
        self.conn = conn
        self.settings = settings
        self.actor = actor
        self.out = out
        self.service = BookingService(conn, settings, actor)


def _range_opts(p):
    p.add_argument("--day")
    p.add_argument("--week", metavar="DAY", help="the week (Monday to Sunday) around DAY")
    p.add_argument("--from", dest="first", metavar="DAY")
    p.add_argument("--to", dest="last", metavar="DAY", help="inclusive")


def build_parser():
    p = argparse.ArgumentParser(prog="roombook", description="Meeting room bookings.")
    p.add_argument("--db", help="database file (default: the db_path setting)")
    p.add_argument("--config", help="settings file (default: $ROOMBOOK_CONFIG or ./roombook.ini)")
    p.add_argument("--user", help="who is running this (default: $ROOMBOOK_USER or the login name)")
    sub = p.add_subparsers(dest="command", required=True)

    s = sub.add_parser("book", help="book a room")
    s.add_argument("room")
    s.add_argument("start", help="'2030-01-07 09:00', 'tomorrow 9:30', ...")
    s.add_argument("duration", help="90m, 1h30, 1.5h")
    s.add_argument("--title", default="")
    s.add_argument("--people", type=int, default=1)
    s.add_argument("--for", dest="for_", metavar="NAME", help="book for someone else (desk, admin)")
    s.set_defaults(handler=commands.cmd_book)

    s = sub.add_parser("cancel", help="cancel a booking")
    s.add_argument("id")
    s.set_defaults(handler=commands.cmd_cancel)

    s = sub.add_parser("move", help="move a booking to another time")
    s.add_argument("id")
    s.add_argument("start")
    s.add_argument("--length", help="new duration (default: keep it)")
    s.set_defaults(handler=commands.cmd_move)

    s = sub.add_parser("show", help="one booking in full")
    s.add_argument("id")
    s.set_defaults(handler=commands.cmd_show)

    s = sub.add_parser("list", help="bookings by day")
    _range_opts(s)
    s.add_argument("--room")
    s.add_argument("--format", choices=("text", "tsv"), default="text")
    s.set_defaults(handler=commands.cmd_list)

    s = sub.add_parser("mine", help="your upcoming bookings")
    s.add_argument("--owner", help="someone else's (anyone may look)")
    s.add_argument("--limit", type=int, default=50)
    s.set_defaults(handler=commands.cmd_mine)

    s = sub.add_parser("free", help="free time in a room")
    s.add_argument("room")
    s.add_argument("--day", default="today")
    s.add_argument("--length", default="30m")
    s.set_defaults(handler=commands.cmd_free)

    s = sub.add_parser("series", help="the same booking every week")
    s.add_argument("room")
    s.add_argument("start")
    s.add_argument("duration")
    s.add_argument("--weeks", type=int, required=True)
    s.add_argument("--title", default="")
    s.add_argument("--people", type=int, default=1)
    s.set_defaults(handler=commands.cmd_series)

    s = sub.add_parser("rooms", help="list, add or load rooms")
    rs = s.add_subparsers(dest="rooms_cmd", required=True)
    rs.add_parser("list")
    a = rs.add_parser("add")
    a.add_argument("code")
    a.add_argument("--name", default="")
    a.add_argument("--capacity", type=int, default=4)
    a.add_argument("--features", default="")
    ld = rs.add_parser("load")
    ld.add_argument("file")
    s.set_defaults(handler=admin.cmd_rooms)

    s = sub.add_parser("import", help="import the facilities spreadsheet (semicolon CSV)")
    s.add_argument("file")
    s.set_defaults(handler=admin.cmd_import)

    s = sub.add_parser("backup", help="write a JSON backup")
    s.add_argument("file")
    s.set_defaults(handler=admin.cmd_backup)

    s = sub.add_parser("restore", help="load a JSON backup")
    s.add_argument("file")
    s.add_argument("--replace", action="store_true", help="overwrite a database that holds data")
    s.set_defaults(handler=admin.cmd_restore)

    s = sub.add_parser("usage", help="monthly usage per room")
    s.add_argument("month", help="YYYY-MM")
    s.add_argument("--format", choices=("text", "tsv"), default="text")
    s.set_defaults(handler=admin.cmd_usage)

    s = sub.add_parser("export", help="finance CSV")
    _range_opts(s)
    s.add_argument("--out")
    s.set_defaults(handler=admin.cmd_export)

    s = sub.add_parser("status", help="which rooms are busy now")
    s.add_argument("--at", help="another moment than now")
    s.set_defaults(handler=admin.cmd_status)

    s = sub.add_parser("log", help="the audit log")
    s.add_argument("--id", help="only this booking")
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(handler=maint.cmd_log)

    s = sub.add_parser("doctor", help="look for double bookings and other damage")
    s.set_defaults(handler=maint.cmd_doctor)

    s = sub.add_parser("purge", help="delete bookings that ended before a day (admin)")
    s.add_argument("--before", required=True)
    s.set_defaults(handler=maint.cmd_purge)

    s = sub.add_parser("calendar", help="iCalendar feed of one room")
    s.add_argument("room")
    _range_opts(s)
    s.set_defaults(handler=maint.cmd_calendar)

    s = sub.add_parser("digest", help="one line per room for a day")
    s.add_argument("--day", default="today")
    s.set_defaults(handler=maint.cmd_digest)
    return p


def _actor(args):
    return args.user or os.environ.get("ROOMBOOK_USER") or getpass.getuser()


def main(argv=None, stdout=None, stderr=None):
    out = Out(stdout, stderr)
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        # argparse already printed why.
        return int(e.code or 0) if isinstance(e.code, int) else 2
    try:
        settings = settings_mod.load(args.config)
    except (OSError, ValueError) as e:
        out.error(f"settings: {e}")
        return 2
    for note in settings.notes:
        out.warn(f"settings: {note}")
    conn = open_db(args.db or settings.db_path)
    try:
        app = App(conn, settings, _actor(args), out)
        return args.handler(args, app)
    except Refused as e:
        out.refused(e.verdicts)
        return e.exit_code
    except RoombookError as e:
        out.error(str(e))
        return e.exit_code
    finally:
        conn.close()
