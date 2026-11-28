"""Rooms. A room code is short and upper case (A, B, 3F-EAST); the name is for people."""
from dataclasses import dataclass, field

from ..errors import UsageError


@dataclass
class Room:
    code: str
    name: str = ""
    capacity: int = 4
    features: tuple = field(default_factory=tuple)

    def label(self):
        return f"{self.code} ({self.name})" if self.name else self.code

    def has(self, feature):
        return feature.lower() in (f.lower() for f in self.features)


def norm_code(code):
    code = (code or "").strip().upper()
    if not code or len(code) > 12 or not all(c.isalnum() or c == "-" for c in code):
        raise UsageError(f"bad room code {code!r}: letters, digits and '-', at most 12")
    return code


def features_from_text(text):
    return tuple(sorted({f.strip().lower() for f in (text or "").split(",") if f.strip()}))


def features_to_text(features):
    return ",".join(features)
