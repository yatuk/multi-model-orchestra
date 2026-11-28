"""Schema versions. The version lives in PRAGMA user_version.

  1  first release: rooms and bookings
  2  rooms.features, bookings.attendees and bookings.series_id, the series and audit tables
  3  cancelled bookings are kept: bookings.status, cancelled_at, cancelled_by, cancel_reason;
     every stored timestamp rewritten as 'YYYY-MM-DD HH:MM' (imports and series wrote other forms)

A new database is created at CURRENT directly. An older one is upgraded one step at a
time, each step in its own transaction, so a failed step leaves the previous version.
"""

CURRENT = 3

SCHEMA = """
CREATE TABLE rooms (
    code      TEXT PRIMARY KEY,
    name      TEXT NOT NULL DEFAULT '',
    capacity  INTEGER NOT NULL DEFAULT 4,
    features  TEXT NOT NULL DEFAULT ''
);
CREATE TABLE series (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    room       TEXT NOT NULL,
    title      TEXT NOT NULL DEFAULT '',
    owner      TEXT NOT NULL,
    weeks      INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE bookings (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    room       TEXT NOT NULL REFERENCES rooms(code),
    starts_at  TEXT NOT NULL,
    ends_at    TEXT NOT NULL,
    owner      TEXT NOT NULL,
    title      TEXT NOT NULL DEFAULT '',
    source     TEXT NOT NULL DEFAULT 'manual',
    attendees  INTEGER NOT NULL DEFAULT 1,
    series_id  INTEGER REFERENCES series(id),
    status     TEXT NOT NULL DEFAULT 'active',
    cancelled_at  TEXT,
    cancelled_by  TEXT,
    cancel_reason TEXT NOT NULL DEFAULT ''
);
CREATE INDEX bookings_room_start ON bookings(room, starts_at);
CREATE TABLE audit (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    at         TEXT NOT NULL,
    actor      TEXT NOT NULL,
    action     TEXT NOT NULL,
    booking_id INTEGER,
    detail     TEXT NOT NULL DEFAULT ''
);
"""


def version(conn):
    return conn.execute("PRAGMA user_version").fetchone()[0]


def _set_version(conn, v):
    # PRAGMA does not take parameters; v is always one of our own ints.
    conn.execute(f"PRAGMA user_version = {int(v)}")


def _has_table(conn, name):
    row = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone()
    return row is not None


def _v1_to_v2(conn):
    conn.execute("ALTER TABLE rooms ADD COLUMN features TEXT NOT NULL DEFAULT ''")
    conn.execute("ALTER TABLE bookings ADD COLUMN attendees INTEGER NOT NULL DEFAULT 1")
    conn.execute("ALTER TABLE bookings ADD COLUMN series_id INTEGER REFERENCES series(id)")
    conn.execute("""CREATE TABLE series (
        id INTEGER PRIMARY KEY AUTOINCREMENT, room TEXT NOT NULL, title TEXT NOT NULL DEFAULT '',
        owner TEXT NOT NULL, weeks INTEGER NOT NULL, created_at TEXT NOT NULL)""")
    conn.execute("CREATE INDEX IF NOT EXISTS bookings_room_start ON bookings(room, starts_at)")
    conn.execute("""CREATE TABLE audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL, actor TEXT NOT NULL,
        action TEXT NOT NULL, booking_id INTEGER, detail TEXT NOT NULL DEFAULT '')""")


def _v2_to_v3(conn):
    conn.execute("ALTER TABLE bookings ADD COLUMN status TEXT NOT NULL DEFAULT 'active'")
    conn.execute("ALTER TABLE bookings ADD COLUMN cancelled_at TEXT")
    conn.execute("ALTER TABLE bookings ADD COLUMN cancelled_by TEXT")
    conn.execute("ALTER TABLE bookings ADD COLUMN cancel_reason TEXT NOT NULL DEFAULT ''")
    # Imported rows were stored as 'YYYY-MM-DDTHH:MM' and series rows with seconds; SQL compares
    # the text, so those rows slipped past the overlap checks. Rewrite them in the one format.
    from .codec import canonical
    rows = conn.execute("SELECT id, starts_at, ends_at FROM bookings").fetchall()
    for r in rows:
        s, e = canonical(r[1]), canonical(r[2])
        if (s, e) != (r[1], r[2]):
            conn.execute("UPDATE bookings SET starts_at = ?, ends_at = ? WHERE id = ?", (s, e, r[0]))


STEPS = {1: _v1_to_v2, 2: _v2_to_v3}


def upgrade(conn):
    """Bring the database to CURRENT. Returns the list of versions passed through."""
    v = version(conn)
    if v == 0 and not _has_table(conn, "bookings"):
        with conn:
            conn.executescript(SCHEMA)
            _set_version(conn, CURRENT)
        return [CURRENT]
    if v == 0:
        # Databases from before user_version was set are version 1.
        v = 1
    if v > CURRENT:
        raise RuntimeError(f"database is version {v}, this roombook knows up to {CURRENT}; upgrade roombook")
    passed = []
    while v < CURRENT:
        step = STEPS[v]
        with conn:
            step(conn)
            _set_version(conn, v + 1)
        v += 1
        passed.append(v)
    return passed
