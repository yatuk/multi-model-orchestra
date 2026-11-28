"""Visible tests, written against the NEW interface (see the brief). Happy path only."""
import unittest
from datetime import datetime

from evlog import ParseOptions, in_window, merge, parse_events, summarize, tail, top_messages

LOG = [
    "2026-03-01T10:00:00 INFO service started\n",
    "2026-03-01T10:05:00 DEBUG cache warm\n",
    "2026-03-01T10:20:00 WARN disk almost full\n",
    "2026-03-01T11:00:00 INFO service started\n",
]


class VisibleTests(unittest.TestCase):
    def test_parse_default_options(self):
        events = list(parse_events(LOG))
        self.assertEqual([e.level for e in events], ["INFO", "DEBUG", "WARN", "INFO"])
        self.assertEqual(events[2].time, datetime(2026, 3, 1, 10, 20))
        self.assertEqual(events[2].line, 3)

    def test_parse_with_options(self):
        events = list(parse_events(LOG, ParseOptions(min_level="WARN")))
        self.assertEqual([e.message for e in events], ["disk almost full"])

    def test_summarize(self):
        s = summarize(LOG)
        self.assertEqual(s["total"], 4)
        self.assertEqual(s["by_level"], {"DEBUG": 1, "INFO": 2, "WARN": 1, "ERROR": 0})
        self.assertEqual((s["first"], s["last"]), ("2026-03-01T10:00:00", "2026-03-01T11:00:00"))

    def test_window_and_top(self):
        got = list(in_window(LOG, datetime(2026, 3, 1, 10, 5), datetime(2026, 3, 1, 11, 0)))
        self.assertEqual([e.line for e in got], [2, 3])
        self.assertEqual(top_messages(LOG, 1, ParseOptions(min_level="INFO")), [("service started", 2)])

    def test_tail_and_merge(self):
        self.assertEqual([e.line for e in tail(LOG, 2, ParseOptions(min_level="INFO"))], [3, 4])
        got = merge([LOG[:2], LOG[2:]], ParseOptions())
        self.assertEqual([(i, e.line) for i, e in got], [(0, 1), (0, 2), (1, 1), (1, 2)])


if __name__ == "__main__":
    unittest.main()
