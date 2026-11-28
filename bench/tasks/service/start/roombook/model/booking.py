"""A booking: one room, one span of time, one owner."""
from dataclasses import dataclass, replace
from datetime import timedelta

from ..util.ids import format_id
from ..util.timefmt import fmt_span

# Where a booking came from. "import" rows came from the facilities spreadsheet.
SOURCES = ("manual", "series", "import", "restore")


@dataclass
class Booking:
    room: str
    start: object          # datetime, naive local time, whole minutes
    end: object            # datetime, after start
    owner: str
    title: str = ""
    attendees: int = 1
    id: int = None
    series_id: int = None
    source: str = "manual"

    @property
    def label(self):
        return format_id(self.id) if self.id is not None else "(new)"

    @property
    def minutes(self):
        return int((self.end - self.start).total_seconds() // 60)

    @property
    def day(self):
        return self.start.date()

    def overlaps(self, start, end):
        # Half-open spans: a booking ending at 10:00 does not touch one starting at 10:00.
        return self.start < end and start < self.end

    def moved(self, start, minutes=None):
        minutes = self.minutes if minutes is None else minutes
        return replace(self, start=start, end=start + timedelta(minutes=minutes))

    def span_text(self):
        return fmt_span(self.start, self.end)

    def sort_key(self):
        return (self.start, self.room, self.id or 0)


def new_booking(room, start, minutes, owner, title="", attendees=1, source="manual"):
    return Booking(room=room, start=start, end=start + timedelta(minutes=minutes),
                   owner=owner, title=title, attendees=attendees, source=source)
