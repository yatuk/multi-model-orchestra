"""Rule plumbing. A rule is a function (booking, ctx) -> list of Verdicts, registered with @rule.

Rules run in registration order and all of them run, so a refusal lists every problem at
once instead of making people retry one fix at a time.
"""
from dataclasses import dataclass

ERROR = "error"
WARNING = "warning"


@dataclass
class Verdict:
    rule: str
    level: str
    message: str

    @property
    def is_error(self):
        return self.level == ERROR


@dataclass
class Context:
    bookings: object        # BookingStore
    rooms: dict             # code -> Room
    settings: object
    now: object
    actor: str
    kind: str = "book"      # book | move | series


_REGISTRY = []


def rule(name, kinds=("book", "move", "series")):
    def wrap(fn):
        _REGISTRY.append((name, tuple(kinds), fn))
        fn.rule_name = name
        return fn
    return wrap


def registered():
    return list(_REGISTRY)


def error(name, message):
    return Verdict(name, ERROR, message)


def warning(name, message):
    return Verdict(name, WARNING, message)
