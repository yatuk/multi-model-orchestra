"""Import of the facilities team's spreadsheet export.

The export is a semicolon separated file (their spreadsheet runs with a European locale):

    Room;Date;From;To;Organiser;Subject;People
    A;07.01.2030;09:00;10:30;alice;Planning;6

Date is DD.MM.YYYY, times are HH:MM or H.MM. People may be empty (then 1). Lines starting
with '#' and empty lines are skipped. A bad line is reported with its line number and the
rest of the file is still read.
"""
import csv
import io
from dataclasses import dataclass, field
from datetime import datetime

from ..model.room import norm_code
from ..errors import UsageError

HEADER = ["room", "date", "from", "to", "organiser", "subject", "people"]


@dataclass
class ImportResult:
    rows: list = field(default_factory=list)
    problems: list = field(default_factory=list)   # (line number, message)


def _time(day, text):
    text = text.strip().replace(".", ":")
    h, _, m = text.partition(":")
    if not (h.isdigit() and m.isdigit() and len(m) == 2):
        raise ValueError(f"bad time {text!r}")
    return day.replace(hour=int(h), minute=int(m))


def _day(text):
    return datetime.strptime(text.strip(), "%d.%m.%Y")


def _header_ok(cells):
    return [c.strip().lower() for c in cells][: len(HEADER)] == HEADER


def parse_rows(text, known_rooms=None):
    """Rows ready for the store, plus problems. known_rooms: room codes that exist."""
    result = ImportResult()
    reader = csv.reader(io.StringIO(text), delimiter=";")
    header_seen = False
    for lineno, cells in enumerate(reader, start=1):
        if not cells or not "".join(cells).strip() or cells[0].lstrip().startswith("#"):
            continue
        if not header_seen:
            if not _header_ok(cells):
                raise UsageError("the file does not start with the header " + ";".join(h.title() for h in HEADER))
            header_seen = True
            continue
        cells = [c.strip() for c in cells] + [""] * (len(HEADER) - len(cells))
        room, day, frm, to, organiser, subject, people = cells[: len(HEADER)]
        try:
            room = norm_code(room)
            d = _day(day)
            start, end = _time(d, frm), _time(d, to)
        except (ValueError, UsageError) as e:
            result.problems.append((lineno, str(e)))
            continue
        if end <= start:
            result.problems.append((lineno, "ends before it starts"))
            continue
        if known_rooms is not None and room not in known_rooms:
            result.problems.append((lineno, f"unknown room {room}"))
            continue
        if not organiser:
            result.problems.append((lineno, "no organiser"))
            continue
        try:
            attendees = int(people) if people else 1
        except ValueError:
            result.problems.append((lineno, f"bad number of people {people!r}"))
            continue
        result.rows.append({
            "room": room,
            # ISO form, as the spreadsheet's own audit export writes it.
            "starts_at": start.isoformat(timespec="minutes"),
            "ends_at": end.isoformat(timespec="minutes"),
            "owner": organiser,
            "title": subject,
            "source": "import",
            "attendees": attendees,
            "line": lineno,
        })
    if not header_seen:
        raise UsageError("empty import file")
    return result


def read_file(path, known_rooms=None):
    # utf-8-sig: the spreadsheet writes a byte order mark.
    with open(path, encoding="utf-8-sig", newline="") as f:
        return parse_rows(f.read(), known_rooms)
