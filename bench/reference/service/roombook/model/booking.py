"""A booking: one room, one span of time, one owner."""
from dataclasses import dataclass, replace
from datetime import timedelta

from ..util.ids import format_id
from ..util.timefmt import fmt_span

# Where a booking came from. "import" rows came from the facilities spreadsheet.
SOURCES = ("manual", "series", "import", "restore")
STATUSES = ("active", "cancelled")


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
    status: str = "active"         # active | cancelled
    cancelled_at: object = None    # datetime, when status became cancelled
    cancelled_by: str = None
    cancel_reason: str = ""

    @property
    def is_cancelled(self):
        return self.status == "cancelled"

    def is_late_cancel(self, notice_hours):
        """Cancelled less than notice_hours before the start (the room could not be given away)."""
        return self.is_cancelled and self.cancelled_at is not None and \
            self.start - self.cancelled_at < timedelta(hours=notice_hours)

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
