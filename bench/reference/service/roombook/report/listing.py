"""The booking listing, for people (text) and for scripts (tsv).

The tsv form is read by other teams' scripts (the screens next to each room, the cleaning
rota). Its columns and their order do not change; new information goes elsewhere.
"""
from ..util.text import shorten, tsv_line
from ..util.timefmt import days, fmt_day, fmt_hm

TSV_HEADER = ("id", "room", "start", "end", "owner", "title")
_TSV_TIME = "%Y-%m-%d %H:%M"


def text_lines(bookings, first, stop):
    by_day = {}
    for b in bookings:
        by_day.setdefault(b.day, []).append(b)
    lines = []
    for d in days(first, stop):
        todays = sorted(by_day.get(d, []), key=lambda b: b.sort_key())
        if not todays and stop - first != _ONE_DAY:
            continue
        lines.append(fmt_day(d))
        if not todays:
            lines.append("  nothing booked")
        for b in todays:
            lines.append(_line(b))
    if not lines:
        lines.append("nothing booked")
    return lines


def _line(b):
    who = b.owner if len(b.owner) <= 10 else b.owner[:10]
    line = f"  {fmt_hm(b.start)}-{fmt_hm(b.end)}  {b.room:<6} {b.label}  {who:<10} {shorten(b.title, 40)}".rstrip()
    return line + "  [cancelled]" if b.is_cancelled else line


def tsv_lines(bookings):
    # Scripts read this: cancelled bookings never appear here, whatever the caller passes.
    lines = [tsv_line(TSV_HEADER)]
    for b in sorted((b for b in bookings if not b.is_cancelled), key=lambda b: b.sort_key()):
        lines.append(tsv_line((b.label, b.room, b.start.strftime(_TSV_TIME), b.end.strftime(_TSV_TIME),
                               b.owner, b.title)))
    return lines


def show_lines(b, room=None):
    lines = [f"Booking {b.label}",
             f"  room:      {room.label() if room else b.room}",
             f"  when:      {b.span_text()}",
             f"  owner:     {b.owner}",
             f"  title:     {b.title}",
             f"  attendees: {b.attendees}",
             f"  source:    {b.source}"]
    if b.series_id:
        lines.append(f"  series:    {b.series_id}")
    lines.append(f"  status:    {b.status}")
    if b.is_cancelled:
        when = f"{b.cancelled_at:%Y-%m-%d %H:%M}" if b.cancelled_at else "?"
        lines.append(f"  cancelled: {when} by {b.cancelled_by or '?'}")
        if b.cancel_reason:
            lines.append(f"  reason:    {b.cancel_reason}")
    return lines


from datetime import timedelta as _td  # noqa: E402  (kept next to its only use)

_ONE_DAY = _td(days=1)
