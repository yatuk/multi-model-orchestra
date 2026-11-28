"""The morning digest for the front desk: one line per room for one day."""
from ..util.text import plural
from ..util.timefmt import fmt_day, fmt_hm, fmt_minutes


def digest_lines(bookings, rooms, day, settings):
    by_room = {}
    for b in bookings:
        if b.day == day:
            by_room.setdefault(b.room, []).append(b)
    lines = [f"Digest {fmt_day(day)}"]
    open_min = settings.open_minutes_per_day()
    for room in rooms:
        todays = sorted(by_room.get(room.code, []), key=lambda b: b.start)
        if not todays:
            lines.append(f"  {room.code:<6} free all day")
            continue
        booked = sum(b.minutes for b in todays)
        big = max(b.attendees for b in todays)
        line = (f"  {room.code:<6} {plural(len(todays), 'booking')}, {fmt_minutes(booked)} booked, "
                f"{fmt_hm(todays[0].start)}-{fmt_hm(todays[-1].end)}")
        if big > room.capacity:
            line += f", over capacity ({big} for {room.capacity})"
        if booked >= open_min:
            line += ", full"
        lines.append(line)
    return lines
