"""Turning a weekly series into its bookings."""
from datetime import timedelta

from ..errors import UsageError
from ..model.booking import Booking
from ..model.series import MAX_WEEKS


def expand(series):
    if not 1 <= series.weeks <= MAX_WEEKS:
        raise UsageError(f"a series runs 1 to {MAX_WEEKS} weeks")
    out = []
    for start in series.starts():
        out.append(Booking(room=series.room, start=start, end=start + timedelta(minutes=series.minutes),
                           owner=series.owner, title=series.title, attendees=series.attendees,
                           source="series"))
    return out
