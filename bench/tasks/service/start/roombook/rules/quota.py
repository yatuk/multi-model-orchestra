"""Weekly quota: how many hours one person may hold in one week (Monday to Sunday).

Off when weekly_quota_hours is 0, which is the default. The building turns it on in the
weeks before the end of the year, when the big rooms run out.
"""
from ..util.timefmt import fmt_minutes, week_of
from .base import error, rule


def held_minutes(bookings, owner, day, exclude_id=None):
    first, stop = week_of(day)
    return sum(b.minutes for b in bookings.between(first, stop)
               if b.owner == owner and b.id != exclude_id)


@rule("quota")
def weekly_quota(b, ctx):
    limit_h = ctx.settings.weekly_quota_hours
    if not limit_h:
        return []
    held = held_minutes(ctx.bookings, b.owner, b.day, exclude_id=b.id)
    if held + b.minutes > limit_h * 60:
        monday, _ = week_of(b.day)
        return [error("quota", f"{b.owner} would hold {fmt_minutes(held + b.minutes)} in the week of "
                               f"{monday.isoformat()}; the limit is {limit_h}h")]
    return []
