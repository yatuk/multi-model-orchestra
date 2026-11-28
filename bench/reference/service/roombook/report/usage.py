"""Monthly usage per room.

  bookings  how many bookings started in the month
  hours     their total length in hours, one decimal
  use       hours as a share of the room's open hours on weekdays in that month
  cancelled how many bookings in the month were cancelled

A late cancellation (less than late_cancel_hours before the start, measured when it was
cancelled) still counts in bookings and hours: the room could not be given to anyone else.

Rooms without bookings are listed with zeros, so the report always has every room.
"""
from dataclasses import dataclass

from ..util.text import percent, render_table, tsv_line
from ..util.timefmt import days


@dataclass
class UsageRow:
    room: str
    bookings: int = 0
    minutes: int = 0
    open_minutes: int = 0
    cancelled: int = 0

    @property
    def hours(self):
        return f"{self.minutes / 60:.1f}"

    @property
    def use(self):
        return percent(self.minutes, self.open_minutes)


def weekdays(first, stop):
    return sum(1 for d in days(first, stop) if d.weekday() < 5)


def monthly(bookings, room_codes, first, stop, settings):
    open_minutes = weekdays(first, stop) * settings.open_minutes_per_day()
    rows = {code: UsageRow(code, open_minutes=open_minutes) for code in room_codes}
    for b in bookings:
        row = rows.get(b.room)
        if row is None:
            continue
        if b.is_cancelled:
            row.cancelled += 1
            if not b.is_late_cancel(settings.late_cancel_hours):
                continue
        row.bookings += 1
        row.minutes += b.minutes
    return [rows[c] for c in sorted(rows)]


HEADERS = ("room", "bookings", "hours", "use", "cancelled")


def text_lines(rows, title):
    table = render_table(HEADERS, [(r.room, r.bookings, r.hours, r.use, r.cancelled) for r in rows],
                         right=(1, 2, 3, 4))
    total = sum(r.minutes for r in rows)
    return [title, ""] + table + ["", f"total {total / 60:.1f} hours"]


def tsv_lines(rows):
    return [tsv_line(HEADERS)] + [tsv_line((r.room, r.bookings, r.hours, r.use, r.cancelled)) for r in rows]
