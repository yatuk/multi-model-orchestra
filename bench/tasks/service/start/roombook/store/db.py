"""Opening the database. Callers close what they open (Windows keeps open files locked)."""
import sqlite3
from contextlib import contextmanager

from . import migrate


def open_db(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    migrate.upgrade(conn)
    return conn


@contextmanager
def opened(path):
    conn = open_db(path)
    try:
        yield conn
    finally:
        conn.close()


def is_empty(conn):
    return conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0] == 0 and \
        conn.execute("SELECT COUNT(*) FROM rooms").fetchone()[0] == 0
