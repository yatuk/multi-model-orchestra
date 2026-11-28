"""Bookings in sqlite. Every query returns Booking objects in time order."""
from ..model.booking import Booking
from .codec import canonical, day_key, day_start, from_db, to_db

_COLS = ("id, room, starts_at, ends_at, owner, title, source, attendees, series_id, "
         "status, cancelled_at, cancelled_by, cancel_reason")
# Cancelled bookings stay in the table for history; every query that asks "what is booked"
# leaves them out. Only get(), all() and the include_cancelled readers return them.
_ACTIVE = "status = 'active'"


class BookingStore:
    def __init__(self, conn):
        self.conn = conn

    # --- writing

    def add(self, b):
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO bookings(room, starts_at, ends_at, owner, title, source, attendees, series_id) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (b.room, to_db(b.start), to_db(b.end), b.owner, b.title, b.source, b.attendees, b.series_id))
        b.id = cur.lastrowid
        return b.id

    def add_series(self, series, bookings, created_at):
        """The series row and all its bookings in one transaction: no half-created series."""
        with self.conn:
            cur = self.conn.execute(
                "INSERT INTO series(room, title, owner, weeks, created_at) VALUES (?, ?, ?, ?, ?)",
                (series.room, series.title, series.owner, series.weeks, to_db(created_at)))
            sid = cur.lastrowid
            for b in bookings:
                b.series_id = sid
                c = self.conn.execute(
                    "INSERT INTO bookings(room, starts_at, ends_at, owner, title, source, attendees, series_id) "
                    "VALUES (?, ?, ?, ?, ?, 'series', ?, ?)",
                    (b.room, to_db(b.start), to_db(b.end), b.owner, b.title, b.attendees, sid))
                b.id = c.lastrowid
        return sid

    def bulk_insert(self, rows):
        """Rows already in storage form (dicts with the column names), e.g. from the importer.

        Used for imports of a few thousand rows, where building Booking objects first was slow
        on the old kiosk machines.
        """
        # Whatever form the rows carry, the table holds one timestamp format (see codec).
        rows = [{**r, "starts_at": canonical(r["starts_at"]), "ends_at": canonical(r["ends_at"])} for r in rows]
        with self.conn:
            self.conn.executemany(
                "INSERT INTO bookings(room, starts_at, ends_at, owner, title, source, attendees) "
                "VALUES (:room, :starts_at, :ends_at, :owner, :title, :source, :attendees)", rows)
        return len(rows)

    def insert_with_id(self, b):
        """Restore path: keep the id the booking had in the backup."""
        self.conn.execute(
            "INSERT INTO bookings(id, room, starts_at, ends_at, owner, title, source, attendees, series_id, "
            "status, cancelled_at, cancelled_by, cancel_reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (b.id, b.room, to_db(b.start), to_db(b.end), b.owner, b.title, b.source, b.attendees, b.series_id,
             b.status, to_db(b.cancelled_at) if b.cancelled_at else None, b.cancelled_by, b.cancel_reason or ""))

    def update_times(self, booking_id, start, end):
        with self.conn:
            self.conn.execute("UPDATE bookings SET starts_at = ?, ends_at = ? WHERE id = ?",
                              (to_db(start), to_db(end), booking_id))

    def mark_cancelled(self, booking_id, at, by, reason=""):
        with self.conn:
            self.conn.execute(
                "UPDATE bookings SET status = 'cancelled', cancelled_at = ?, cancelled_by = ?, cancel_reason = ? "
                "WHERE id = ?", (to_db(at), by, reason or "", booking_id))

    def delete_ended_before(self, day):
        with self.conn:
            cur = self.conn.execute("DELETE FROM bookings WHERE ends_at < ?", (day_start(day),))
        return cur.rowcount

    def delete(self, booking_id):
        with self.conn:
            cur = self.conn.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
        return cur.rowcount > 0

    # --- reading

    def get(self, booking_id):
        row = self.conn.execute(f"SELECT {_COLS} FROM bookings WHERE id = ?", (booking_id,)).fetchone()
        return _booking(row) if row else None

    def overlapping(self, room, start, end, exclude_id=None):
        rows = self.conn.execute(
            f"SELECT {_COLS} FROM bookings WHERE {_ACTIVE} AND room = ? AND starts_at < ? AND ends_at > ? "
            "ORDER BY starts_at, id", (room, to_db(end), to_db(start)))
        return [_booking(r) for r in rows if r["id"] != exclude_id]

    def on_day(self, d, room=None, include_cancelled=False):
        sql = f"SELECT {_COLS} FROM bookings WHERE substr(starts_at, 1, 10) = ?"
        if not include_cancelled:
            sql += f" AND {_ACTIVE}"
        args = [day_key(d)]
        if room:
            sql += " AND room = ?"
            args.append(room)
        sql += " ORDER BY starts_at, room, id"
        return [_booking(r) for r in self.conn.execute(sql, args)]

    def between(self, first_day, stop_day, room=None, include_cancelled=False):
        """Bookings starting on first_day up to, not including, stop_day."""
        sql = f"SELECT {_COLS} FROM bookings WHERE starts_at >= ? AND starts_at < ?"
        if not include_cancelled:
            sql += f" AND {_ACTIVE}"
        args = [day_start(first_day), day_start(stop_day)]
        if room:
            sql += " AND room = ?"
            args.append(room)
        sql += " ORDER BY starts_at, room, id"
        return [_booking(r) for r in self.conn.execute(sql, args)]

    def busy_at(self, room, when):
        row = self.conn.execute(
            f"SELECT {_COLS} FROM bookings WHERE {_ACTIVE} AND room = ? AND starts_at <= ? AND ends_at > ? "
            "ORDER BY starts_at LIMIT 1", (room, to_db(when), to_db(when))).fetchone()
        return _booking(row) if row else None

    def next_start(self, room, when):
        row = self.conn.execute(
            f"SELECT {_COLS} FROM bookings WHERE {_ACTIVE} AND room = ? AND starts_at > ? ORDER BY starts_at LIMIT 1",
            (room, to_db(when))).fetchone()
        return _booking(row) if row else None

    def upcoming_for(self, owner, now):
        rows = self.conn.execute(
            f"SELECT {_COLS} FROM bookings WHERE {_ACTIVE} AND owner = ? AND ends_at > ? ORDER BY starts_at, id",
            (owner, to_db(now)))
        return [_booking(r) for r in rows]

    def in_series(self, series_id):
        rows = self.conn.execute(f"SELECT {_COLS} FROM bookings WHERE {_ACTIVE} AND series_id = ? ORDER BY starts_at",
                                 (series_id,))
        return [_booking(r) for r in rows]

    def all(self):
        """Every row, cancelled ones included (backups need them)."""
        return [_booking(r) for r in self.conn.execute(f"SELECT {_COLS} FROM bookings ORDER BY id")]

    def count(self):
        return self.conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]


def _booking(row):
    return Booking(id=row["id"], room=row["room"], start=from_db(row["starts_at"]),
                   end=from_db(row["ends_at"]), owner=row["owner"], title=row["title"],
                   source=row["source"], attendees=row["attendees"], series_id=row["series_id"],
                   status=row["status"], cancelled_at=from_db(row["cancelled_at"]),
                   cancelled_by=row["cancelled_by"], cancel_reason=row["cancel_reason"] or "")
