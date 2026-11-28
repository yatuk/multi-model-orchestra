"""A weekly series: the same room and time on N consecutive weeks."""
from dataclasses import dataclass
from datetime import timedelta

MAX_WEEKS = 52


@dataclass
class Series:
    room: str
    first_start: object
    minutes: int
    weeks: int
    owner: str
    title: str = ""
    attendees: int = 1

    def starts(self):
        for i in range(self.weeks):
            yield self.first_start + timedelta(weeks=i)
