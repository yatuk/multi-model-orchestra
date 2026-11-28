"""What the commands do, without the printing. One BookingService per command run.

The actor is the person running the command. People manage their own bookings; desk and
admin (see settings, [people]) manage everyone's.
"""
from dataclasses import dataclass, field
from datetime import timedelta

from . import clock, notify
from .errors import NotFound, PermissionDenied, Refused, UsageError
from .model.booking import new_booking
from .model.room import norm_code
from .model.series import Series
from .parse import csvimport
from .rules import Context, check, errors, warnings
from .sched.recur import expand
from .store.audit import AuditLog
from .store.bookings import BookingStore
from .store.codec import from_db
from .store.rooms import RoomStore
from .util.ids import format_id


@dataclass
class ImportSummary:
    imported: int = 0
    skipped: list = field(default_factory=list)     # (line, message)
    problems: list = field(default_factory=list)    # (line, message)


@dataclass
class RoomState:
    room: object
    current: object = None      # the booking in progress, if any
    upcoming: object = None     # the next booking today, if any


class BookingService:
    def __init__(self, conn, settings, actor):
        self.conn = conn
        self.settings = settings
        self.actor = actor
        self.bookings = BookingStore(conn)
        self.rooms = RoomStore(conn)
        self.audit = AuditLog(conn)

    def _log(self, action, booking_id=None, detail=""):
        self.audit.record(clock.now(), self.actor, action, booking_id, detail)

    def _ctx(self, kind):
        return Context(bookings=self.bookings, rooms=self.rooms.by_code(), settings=self.settings,
                       now=clock.now(), actor=self.actor, kind=kind)

    def _get(self, booking_id):
        b = self.bookings.get(booking_id)
        if b is None:
            raise NotFound(f"no such booking {format_id(booking_id)}")
        return b

    def _may_manage(self, b, verb):
        if not self.settings.can_manage(self.actor, b.owner):
            raise PermissionDenied(f"{self.actor} may not {verb} {b.label}: it belongs to {b.owner}")

    # --- single bookings

    def book(self, room, start, minutes, title="", attendees=1, owner=None):
        owner = owner or self.actor
        if owner != self.actor and self.settings.role_of(self.actor) not in ("desk", "admin"):
            raise PermissionDenied(f"{self.actor} may not book for {owner}")
        b = new_booking(norm_code(room), start, minutes, owner, title, attendees)
        verdicts = check(b, self._ctx("book"))
        if errors(verdicts):
            raise Refused(errors(verdicts))
        self.bookings.add(b)
        self._log("book", b.id, f"{b.room} {b.span_text()}" + (f" for {owner}" if owner != self.actor else ""))
        return b, warnings(verdicts)

    def show(self, booking_id):
        return self._get(booking_id)

    def cancel(self, booking_id, reason=""):
        """Cancel a booking: it stays, marked cancelled, and no longer holds the room.

        Returns (booking, late): late when within the notice period (late_cancel_hours).
        """
        b = self._get(booking_id)
        self._may_manage(b, "cancel")
        if b.is_cancelled:
            raise UsageError(f"{b.label} is already cancelled")
        now = clock.now()
        if b.start <= now:
            raise UsageError(f"{b.label} has already started")
        late = b.start - now < timedelta(hours=self.settings.late_cancel_hours)
        self.bookings.mark_cancelled(b.id, now, self.actor, reason)
        b.status, b.cancelled_at, b.cancelled_by, b.cancel_reason = "cancelled", now, self.actor, reason or ""
        self._log("cancel", b.id, f"{b.room} {b.span_text()}" + (" (late)" if late else "")
                  + (f": {reason}" if reason else ""))
        notify.tell_owner(self.settings, "cancelled", b, self.actor, f"Reason: {reason}" if reason else "")
        return b, late

    def move(self, booking_id, start, minutes=None):
        b = self._get(booking_id)
        self._may_manage(b, "move")
        if b.is_cancelled:
            raise UsageError(f"{b.label} is cancelled; book again instead")
        moved = b.moved(start, minutes)
        verdicts = check(moved, self._ctx("move"))
        if errors(verdicts):
            raise Refused(errors(verdicts))
        self.bookings.update_times(b.id, moved.start, moved.end)
        self._log("move", b.id, f"{b.span_text()} -> {moved.span_text()}")
        notify.tell_owner(self.settings, "moved", moved, self.actor, f"It was {b.span_text()} before.")
        return moved, warnings(verdicts)

    def upcoming_for(self, owner):
        return self.bookings.upcoming_for(owner, clock.now())

    # --- many bookings

    def series(self, room, first_start, minutes, weeks, title="", attendees=1):
        s = Series(room=norm_code(room), first_start=first_start, minutes=minutes, weeks=weeks,
                   owner=self.actor, title=title, attendees=attendees)
        ctx = self._ctx("series")
        ok, skipped = [], []
        for b in expand(s):
            errs = errors(check(b, ctx))
            if errs:
                skipped.append((b, errs))
            else:
                ok.append(b)
        if not ok:
            raise Refused([e for _, errs in skipped for e in errs][:5])
        sid = self.bookings.add_series(s, ok, clock.now())
        self._log("series", ok[0].id, f"series {sid}: {len(ok)} of {s.weeks} weeks in {s.room}")
        return ok, skipped

    def import_file(self, path):
        if self.settings.role_of(self.actor) not in ("desk", "admin"):
            raise PermissionDenied("only desk and admin may import")
        parsed = csvimport.read_file(path, known_rooms=set(self.rooms.codes()))
        summary = ImportSummary(problems=parsed.problems)
        accepted = []
        for row in parsed.rows:
            start, end = from_db(row["starts_at"]), from_db(row["ends_at"])
            clash = self.bookings.overlapping(row["room"], start, end)
            if clash:
                summary.skipped.append((row.get("line"), f"{row['room']} {start:%Y-%m-%d %H:%M} "
                                        f"overlaps {clash[0].label}"))
                continue
            mine = [r for r in accepted if r["room"] == row["room"] and
                    from_db(r["starts_at"]) < end and start < from_db(r["ends_at"])]
            if mine:
                summary.skipped.append((row.get("line"), f"{row['room']} {start:%Y-%m-%d %H:%M} "
                                        "overlaps another line of the same file"))
                continue
            accepted.append(row)
        summary.imported = self.bookings.bulk_insert(accepted)
        self._log("import", None, f"{summary.imported} rows from {path}")
        return summary

    def purge(self, before_day):
        """Delete bookings that ended before before_day. The audit log keeps them."""
        n = self.bookings.delete_ended_before(before_day)
        self._log("purge", None, f"{n} bookings ended before {before_day.isoformat()}")
        return n

    # --- rooms right now

    def status(self, when=None):
        when = when or clock.now()
        out = []
        for room in self.rooms.all():
            current = self.bookings.busy_at(room.code, when)
            upcoming = self.bookings.next_start(room.code, when)
            if upcoming and upcoming.start.date() != when.date():
                upcoming = None
            out.append(RoomState(room=room, current=current, upcoming=upcoming))
        return out
