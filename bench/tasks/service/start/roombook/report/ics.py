"""An iCalendar feed of one room, for the screen next to the door and for people's calendars.

Kept to what every calendar program reads: VEVENT with UID, DTSTAMP, DTSTART, DTEND and
SUMMARY. Times are floating local times (no time zone), which is what the building uses.
Lines end with CRLF, as the format requires.
"""
from .. import clock

_TS = "%Y%m%dT%H%M%S"


def _escape(text):
    return (text or "").replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _fold(line):
    # Lines longer than 75 octets are folded: CRLF and one space.
    out = []
    while len(line.encode("utf-8")) > 75:
        cut = 75
        while len(line[:cut].encode("utf-8")) > 75:
            cut -= 1
        out.append(line[:cut])
        line = " " + line[cut:]
    out.append(line)
    return out


def feed(bookings, room, calname=None):
    stamp = clock.now().strftime(_TS)
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//roombook//EN",
             f"X-WR-CALNAME:{_escape(calname or room.label())}"]
    for b in sorted(bookings, key=lambda b: b.sort_key()):
        if b.room != room.code:
            continue
        summary = b.title or f"booked by {b.owner}"
        lines += ["BEGIN:VEVENT", f"UID:{b.label}@roombook", f"DTSTAMP:{stamp}",
                  f"DTSTART:{b.start.strftime(_TS)}", f"DTEND:{b.end.strftime(_TS)}",
                  f"SUMMARY:{_escape(summary)}", f"ORGANIZER;CN={_escape(b.owner)}:invalid:nomail",
                  "END:VEVENT"]
    lines.append("END:VCALENDAR")
    folded = []
    for line in lines:
        folded.extend(_fold(line))
    return "\r\n".join(folded) + "\r\n"
