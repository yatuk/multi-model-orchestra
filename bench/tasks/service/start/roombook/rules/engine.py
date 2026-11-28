from . import builtin, quota  # noqa: F401  (registers the rules)
from .base import registered


def check(booking, ctx, skip=()):
    """Every verdict for booking, errors and warnings, in rule order."""
    out = []
    for name, kinds, fn in registered():
        if name in skip or ctx.kind not in kinds:
            continue
        out.extend(fn(booking, ctx))
    return out


def errors(verdicts):
    return [v for v in verdicts if v.is_error]


def warnings(verdicts):
    return [v for v in verdicts if not v.is_error]
