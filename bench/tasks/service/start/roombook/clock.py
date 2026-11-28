"""The one place that knows what time it is.

Everything in roombook asks clock.now() instead of datetime.now(), so tests (and the
"what if" mode of the kiosk) can freeze time. Times are naive local times, whole minutes.
"""
from datetime import datetime

_frozen = None


def now():
    if _frozen is not None:
        return _frozen
    return datetime.now().replace(second=0, microsecond=0)


def today():
    return now().date()


def freeze(when):
    global _frozen
    _frozen = when.replace(second=0, microsecond=0)


def unfreeze():
    global _frozen
    _frozen = None


def is_frozen():
    return _frozen is not None
