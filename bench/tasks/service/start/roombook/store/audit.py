"""The audit log: who changed which booking, and when.

Every change made through BookingService writes one row here (book, move, cancel, series,
import, purge). Front desk reads it with `roombook log` when someone asks where their
meeting went. Rows are never updated or deleted, not even by purge.
"""
from dataclasses import dataclass

from .codec import from_db, to_db


@dataclass
class AuditEntry:
    at: object
    actor: str
    action: str
    booking_id: int
    detail: str


class AuditLog:
    def __init__(self, conn):
        self.conn = conn

    def record(self, at, actor, action, booking_id=None, detail=""):
        with self.conn:
            self.conn.execute(
                "INSERT INTO audit(at, actor, action, booking_id, detail) VALUES (?, ?, ?, ?, ?)",
                (to_db(at), actor, action, booking_id, detail))

    def recent(self, limit=20, booking_id=None):
        sql = "SELECT at, actor, action, booking_id, detail FROM audit"
        args = []
        if booking_id is not None:
            sql += " WHERE booking_id = ?"
            args.append(booking_id)
        sql += " ORDER BY id DESC LIMIT ?"
        args.append(int(limit))
        rows = self.conn.execute(sql, args).fetchall()
        return [AuditEntry(from_db(r["at"]), r["actor"], r["action"], r["booking_id"], r["detail"])
                for r in reversed(rows)]
