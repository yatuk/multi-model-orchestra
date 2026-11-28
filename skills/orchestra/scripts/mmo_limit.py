"""When does a limited lane come back? Read it from the tool's own error text. Stdlib only.

    python mmo_limit.py PROVIDER PROMPT_FILE FILE [FILE ...]     prints an ISO time (UTC) or nothing

parse_retry_time(text) understands only what real tools print, and refuses to guess:
    "try again at Dec 21st, 2026 9:18 AM"   a full month, day and time; a missing year means the next
                                            such date (local time unless a zone in brackets follows)
    "resets 4pm (Europe/Istanbul)"          a bare hour counts only when a zone is named: the next
                                            time the clock in that zone shows it
    "Retry-After: 120"                      seconds from now (also an HTTP date)
Anything else, a date without a time, a time in the past, or one more than 35 days away returns None.
Lines that only echo the brief are dropped, as the classifier does, so a brief that mentions a date
cannot set a return time.
"""
import datetime
import email.utils
import re
import sys

MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
MAX_DAYS = 35

_MON = r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?"
_TIME = r"(\d{1,2})(?::(\d{2}))?\s*([ap])\.?m\b\.?|(\d{1,2}):(\d{2})"
_ZONE = r"(?:\s*\(([A-Za-z_]+(?:/[A-Za-z_+\-0-9]+)*)\))?"
# "Dec 21st, 2026 9:18 AM" and "Dec 21 at 9:18 AM"
DATE_FIRST = re.compile(r"\b" + _MON + r"\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s+(20\d\d)\b(?!:))?,?(?:\s+at)?\s+(?:" + _TIME + r")" + _ZONE, re.I)
# "21 Dec 2026 9:18 AM"
DAY_FIRST = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+" + _MON + r"(?:,?\s+(20\d\d)\b(?!:))?,?(?:\s+at)?\s+(?:" + _TIME + r")" + _ZONE, re.I)
BARE_TIME = re.compile(r"\bresets?\s+(?:at\s+)?(?:" + _TIME + r")\s*\(([A-Za-z_]+(?:/[A-Za-z_+\-0-9]+)*)\)", re.I)
# Seconds only: "5 minutes" is not read as 5 seconds (any other unit after the number fails the match).
RETRY_AFTER = re.compile(r"retry[- ]after\s*[:=]?\s*(\d{1,7})(?:[ \t]*(?:s|secs?|seconds?)\b)?(?![ \t]*[A-Za-z0-9])", re.I)
RETRY_DATE = re.compile(r"retry[- ]after\s*[:=]\s*([A-Za-z]{3}, \d{1,2} [A-Za-z]{3} \d{4} \d\d:\d\d:\d\d GMT)", re.I)


def _zone(name):
    if not name:
        return None
    if name.upper() in ("UTC", "GMT", "Z"):
        return datetime.timezone.utc
    try:
        import zoneinfo
        return zoneinfo.ZoneInfo(name)
    except Exception:  # unknown zone or no tz database on this machine: do not guess an offset
        return False


def _hm(g):
    """Hour and minute from the six time groups; None when they are not a real clock time."""
    h12, m12, ap, h24, m24 = g
    if h12 is not None:
        h, m = int(h12), int(m12 or 0)
        if not 1 <= h <= 12:
            return None
        return (h % 12) + (12 if ap.lower() == "p" else 0), m
    h, m = int(h24), int(m24)
    return (h, m) if h < 24 and m < 60 else None


def _utc(dt):
    return dt.astimezone(datetime.timezone.utc)


def _final(dt, now):
    if dt is None or not now < dt <= now + datetime.timedelta(days=MAX_DAYS):
        return None
    return _utc(dt).strftime("%Y-%m-%dT%H:%M:%SZ")


def _dated(mon, day, year, tgroups, zname, now):
    hm = _hm(tgroups)
    tz = _zone(zname)
    if hm is None or tz is False:
        return None
    tz = tz or now.astimezone().tzinfo  # no zone named: the tool printed its own local time
    month, day = MONTHS[mon.lower()[:3]], int(day)
    local_now = now.astimezone(tz)
    try:
        if year:
            return _final(datetime.datetime(int(year), month, day, hm[0], hm[1], tzinfo=tz), now)
        dt = datetime.datetime(local_now.year, month, day, hm[0], hm[1], tzinfo=tz)
        if dt <= now:  # no year: the next such date, never one in the past
            dt = datetime.datetime(local_now.year + 1, month, day, hm[0], hm[1], tzinfo=tz)
        return _final(dt, now)
    except ValueError:  # Feb 30 and the like
        return None


def parse_retry_time(text, now=None):
    """ISO time (UTC, ...Z) when the lane comes back, or None when the text does not say with confidence."""
    if not isinstance(text, str) or not text.strip():
        return None
    now = now or datetime.datetime.now(datetime.timezone.utc)
    # An HTTP date first: its day-month-year-time shape would also match the day-first pattern below.
    m = RETRY_DATE.search(text)
    if m:
        try:
            when = email.utils.parsedate_to_datetime(m.group(1))
            return _final(when if when.tzinfo else when.replace(tzinfo=datetime.timezone.utc), now)
        except (TypeError, ValueError):
            return None
    m = DATE_FIRST.search(text)
    if m:
        return _dated(m.group(1), m.group(2), m.group(3), m.groups()[3:8], m.group(9), now)
    m = DAY_FIRST.search(text)
    if m:
        return _dated(m.group(2), m.group(1), m.group(3), m.groups()[3:8], m.group(9), now)
    m = BARE_TIME.search(text)
    if m:
        hm, tz = _hm(m.groups()[:5]), _zone(m.group(6))
        if hm is None or not tz:
            return None
        local = now.astimezone(tz)
        dt = local.replace(hour=hm[0], minute=hm[1], second=0, microsecond=0)
        if dt <= now:
            dt = (local + datetime.timedelta(days=1)).replace(hour=hm[0], minute=hm[1], second=0, microsecond=0)
        return _final(dt, now)
    m = RETRY_AFTER.search(text)
    if m and int(m.group(1)) > 0:
        return _final(now + datetime.timedelta(seconds=int(m.group(1))), now)
    return None


def _read_iso(text):
    try:
        return datetime.datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
    except (TypeError, ValueError):
        return None


def future(iso, now=None):
    """The datetime of a stored return time that is still ahead, else None (also for junk)."""
    when = _read_iso(iso)
    now = now or datetime.datetime.now(datetime.timezone.utc)
    return when if when and when > now else None


def local_text(iso):
    """A stored return time as local "YYYY-MM-DD HH:MM" for people to read; '' when it is junk."""
    when = _read_iso(iso)
    return when.astimezone().strftime("%Y-%m-%d %H:%M") if when else ""


def main(argv):
    if len(argv) < 3:
        print(__doc__, file=sys.stderr)
        return 2
    sys.path.insert(0, __file__.rsplit("/", 1)[0] if "/" in __file__ else ".")
    import mmo_classify

    texts = [mmo_classify.read(p) for p in argv[2:]]
    body = mmo_classify.own_lines(argv[0], mmo_classify.read(argv[1]), texts)
    when = parse_retry_time(body)
    if when:
        sys.stdout.buffer.write((when + "\n").encode("ascii"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
