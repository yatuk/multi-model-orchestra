from ..model.room import Room, features_from_text, features_to_text


class RoomStore:
    def __init__(self, conn):
        self.conn = conn

    def save(self, room):
        """Insert or replace by code."""
        with self.conn:
            self.conn.execute(
                "INSERT INTO rooms(code, name, capacity, features) VALUES (?, ?, ?, ?) "
                "ON CONFLICT(code) DO UPDATE SET name=excluded.name, capacity=excluded.capacity, "
                "features=excluded.features",
                (room.code, room.name, room.capacity, features_to_text(room.features)))

    def get(self, code):
        row = self.conn.execute("SELECT * FROM rooms WHERE code = ?", (code,)).fetchone()
        return _room(row) if row else None

    def all(self):
        return [_room(r) for r in self.conn.execute("SELECT * FROM rooms ORDER BY code")]

    def codes(self):
        return [r[0] for r in self.conn.execute("SELECT code FROM rooms ORDER BY code")]

    def by_code(self):
        return {r.code: r for r in self.all()}


def _room(row):
    return Room(code=row["code"], name=row["name"], capacity=row["capacity"],
                features=features_from_text(row["features"]))
