"""The finance export: one CSV line per booking, for charging rooms back to departments.

Finance loads this file into their own system, which checks the header word for word.
"""
import csv
import io

HEADER = ["booking", "room", "date", "from", "to", "owner", "minutes"]


def finance_csv(bookings):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(HEADER)
    for b in sorted(bookings, key=lambda b: b.sort_key()):
        w.writerow([b.label, b.room, b.start.strftime("%Y-%m-%d"), b.start.strftime("%H:%M"),
                    b.end.strftime("%H:%M"), b.owner, b.minutes])
    return buf.getvalue()
