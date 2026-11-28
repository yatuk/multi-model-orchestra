"""JSON backups. restore() reads every format we ever wrote; dump() writes the newest.

Format 1 (the kiosk era) looked like:
    {"version": 1, "rooms": [{"code", "name", "capacity"}],
     "items": [{"id", "room", "from", "to", "who", "what"}]}
Format 2:
    {"format": 2, "written": "...", "rooms": [{..., "features": [...]}], "series": [...],
     "bookings": [{"id", "room", "start", "end", "owner", "title", "source", "attendees", "series_id"}]}
Times in a backup are 'YYYY-MM-DD HH:MM'.
"""
import json

from .. import clock
from ..errors import RestoreError
from ..model.booking import Booking
from ..model.room import Room
from .bookings import BookingStore
from .codec import from_db, to_db
from .db import is_empty
from .rooms import RoomStore

FORMAT = 2


def dump(conn, path):
    rooms = RoomStore(conn).all()
    bookings = BookingStore(conn).all()
    series = [dict(r) for r in conn.execute("SELECT * FROM series ORDER BY id")]
    data = {
        "format": FORMAT,
        "written": to_db(clock.now()),
        "rooms": [{"code": r.code, "name": r.name, "capacity": r.capacity, "features": list(r.features)}
                  for r in rooms],
        "series": series,
        "bookings": [_booking_out(b) for b in bookings],
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")
    return len(bookings)


def _booking_out(b):
    return {"id": b.id, "room": b.room, "start": to_db(b.start), "end": to_db(b.end), "owner": b.owner,
            "title": b.title, "source": b.source, "attendees": b.attendees, "series_id": b.series_id}


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        raise RestoreError(f"cannot read backup {path}: {e}") from None


def _from_v1(data):
    rooms = [Room(code=r["code"], name=r.get("name", ""), capacity=int(r.get("capacity", 4)))
             for r in data.get("rooms", [])]
    bookings = [Booking(id=i["id"], room=i["room"], start=from_db(i["from"]), end=from_db(i["to"]),
                        owner=i["who"], title=i.get("what", ""), source="restore")
                for i in data.get("items", [])]
    return rooms, [], bookings


def _from_v2(data):
    rooms = [Room(code=r["code"], name=r.get("name", ""), capacity=int(r.get("capacity", 4)),
                  features=tuple(r.get("features", ()))) for r in data.get("rooms", [])]
    bookings = [Booking(id=b["id"], room=b["room"], start=from_db(b["start"]), end=from_db(b["end"]),
                        owner=b["owner"], title=b.get("title", ""), source=b.get("source", "restore"),
                        attendees=int(b.get("attendees", 1)), series_id=b.get("series_id"))
                for b in data.get("bookings", [])]
    return rooms, data.get("series", []), bookings


def restore(conn, path, replace=False):
    """Load a backup. Refuses a database that already holds data unless replace is set."""
    data = _read(path)
    if data.get("version") == 1:
        rooms, series, bookings = _from_v1(data)
    elif data.get("format") == 2:
        rooms, series, bookings = _from_v2(data)
    else:
        raise RestoreError(f"unknown backup format in {path}")
    if not is_empty(conn) and not replace:
        raise RestoreError("the database is not empty; use --replace to overwrite it")
    rs, bs = RoomStore(conn), BookingStore(conn)
    with conn:
        if replace:
            conn.execute("DELETE FROM bookings")
            conn.execute("DELETE FROM series")
            conn.execute("DELETE FROM rooms")
    for r in rooms:
        rs.save(r)
    with conn:
        for s in series:
            conn.execute("INSERT INTO series(id, room, title, owner, weeks, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                         (s["id"], s["room"], s.get("title", ""), s["owner"], s["weeks"], s["created_at"]))
        for b in bookings:
            bs.insert_with_id(b)
    return len(rooms), len(bookings)
