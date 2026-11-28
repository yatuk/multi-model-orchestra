"""Messages to people whose booking someone else changed.

When desk or an admin moves or cancels a booking that belongs to someone else, a short
plain-text message is written to the outbox folder (setting outbox_dir; empty means off).
The mail relay picks files up from there; roombook itself never sends mail. File names
sort by time so the relay sends them in order.
"""
import os

from . import clock

_COUNTER = {"n": 0}


def _name(action, booking):
    _COUNTER["n"] += 1
    return f"{clock.now():%Y%m%d-%H%M}-{_COUNTER['n']:03d}-{action}-{booking.label}.txt"


def message(action, booking, actor, extra=""):
    lines = [f"To: {booking.owner}",
             f"Subject: your booking {booking.label} was {action} by {actor}",
             "",
             f"Room:  {booking.room}",
             f"When:  {booking.span_text()}",
             f"Title: {booking.title}"]
    if extra:
        lines += ["", extra]
    lines += ["", "This message was written by roombook. Ask the front desk if this is unexpected."]
    return "\n".join(lines) + "\n"


def tell_owner(settings, action, booking, actor, extra=""):
    """Write a message when actor is not the owner. Returns the file path or None."""
    folder = settings.get("outbox_dir") or ""
    if not folder or actor == booking.owner:
        return None
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, _name(action, booking))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(message(action, booking, actor, extra))
    return path
