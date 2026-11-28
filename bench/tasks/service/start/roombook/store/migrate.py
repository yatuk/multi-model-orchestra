"""Schema versions. The version lives in PRAGMA user_version.

  1  first release: rooms and bookings
  2  rooms.features, bookings.attendees and bookings.series_id, the series and audit tables

A new database is created at CURRENT directly. An older one is upgraded one step at a
time, each step in its own transaction, so a failed step leaves the previous version.
"""

CURRENT = 2

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
    series_id  INTEGER REFERENCES series(id)
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


STEPS = {1: _v1_to_v2}


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
