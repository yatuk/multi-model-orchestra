"""Which days a listing covers: --day, --week, or --from/--to (to is inclusive)."""
from datetime import timedelta

from ..errors import UsageError
from ..util.timefmt import parse_day, week_of


def day_range(day=None, week=None, first=None, last=None, today=None):
    """(first day, stop day) with stop exclusive. Default: today."""
    given = [x for x in (day, week, first or last) if x]
    if len(given) > 1:
        raise UsageError("use one of --day, --week or --from/--to")
    if week:
        return week_of(parse_day(week, today))
    if first or last:
        a = parse_day(first or last, today)
        b = parse_day(last or first, today)
        if b < a:
            raise UsageError("--to is before --from")
        return a, b + timedelta(days=1)
    d = parse_day(day or "today", today)
    return d, d + timedelta(days=1)
