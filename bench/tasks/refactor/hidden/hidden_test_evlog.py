"""Held-out tests for the refactor task. The lane never sees this file.

Groups (one class each):
  KeepWorking   callers with default arguments and one-shot inputs: pass on the starting
                code, must still pass
  NewInterface  ParseOptions and the new signatures, old positional flags rejected at call time
  Streaming     lazy iterators, flat memory, strict errors in order
  Options       options passed through every caller
Names are reached through the module, so one missing name fails only the tests that use it.
"""
import dataclasses
import inspect
import io
import os
import tempfile
import tracemalloc
import unittest
from datetime import datetime

import evlog
import evlog.cli

PUBLIC = [
    "evlog.parse_events", "evlog.summarize", "evlog.top_messages", "evlog.in_window",
    "evlog.tail", "evlog.merge", "evlog.ParseOptions", "evlog.ParseError", "evlog.reader.ParseOptions",
    "evlog.cli.main",
]

LOG = [
    "2026-03-01T09:58:00 DEBUG boot\n",
    "\n",
    "2026-03-01T10:00:00 INFO request ok\n",
    "garbage line\n",
    "2026-03-01T10:00:00 WARN slow request\r\n",
    "2026-03-01T10:30:00 INFO request ok\n",
    "   \n",
    "2026-03-01T09:00:00 ERROR late arrival\n",
    "2026-03-01T11:00:00 WARN slow request\n",
    "2026-03-01T10:45:00 TRACE noisy\n",
    "2026-03-01T10:50:00 INFO cache cleared",
]
DEFAULT_SUMMARY = {
    "total": 7,
    "by_level": {"DEBUG": 1, "INFO": 3, "WARN": 2, "ERROR": 1},
    "first": "2026-03-01T09:00:00",
    "last": "2026-03-01T11:00:00",
}

# A second source, not in time order, with a malformed line.
LOG_B = [
    "2026-03-01T10:00:00 INFO from b\n",
    "2026-03-01T08:00:00 DEBUG early b\n",
    "bad\n",
    "2026-03-01T10:30:00 ERROR b late\n",
]


def t(h, m=0):
    return datetime(2026, 3, 1, h, m)


class Source:
    """A one-shot line source that counts reads and fails when read past `limit`."""

    def __init__(self, lines, limit=None):
        self.lines, self.limit, self.reads = list(lines), limit, 0

    def __iter__(self):
        for line in self.lines:
            if self.limit is not None and self.reads >= self.limit:
                raise AssertionError(f"read past line {self.limit}: not lazy")
            self.reads += 1
            yield line


class KeepWorking(unittest.TestCase):
    def test_summarize_defaults(self):
        self.assertEqual(evlog.summarize(LOG), DEFAULT_SUMMARY)
        self.assertEqual(evlog.summarize([]), {"total": 0, "by_level": {"DEBUG": 0, "INFO": 0, "WARN": 0, "ERROR": 0},
                                               "first": None, "last": None})

    def test_in_window_defaults(self):
        self.assertEqual([e.line for e in evlog.in_window(LOG, t(10), t(11))], [3, 5, 6, 11])

    def test_top_messages_ties(self):
        self.assertEqual(evlog.top_messages(LOG, 3), [("request ok", 2), ("slow request", 2), ("boot", 1)])

    def test_one_shot_inputs(self):
        # Works on the starting code (it builds a list); a stream that is read twice breaks it.
        self.assertEqual(evlog.summarize(Source(LOG)), DEFAULT_SUMMARY)
        self.assertEqual(evlog.summarize(io.StringIO("".join(LOG))), DEFAULT_SUMMARY)
        self.assertEqual(evlog.top_messages(iter(LOG), 3), [("request ok", 2), ("slow request", 2), ("boot", 1)])

    def test_tail_defaults(self):
        self.assertEqual([e.line for e in evlog.tail(LOG, 3)], [8, 9, 11])
        self.assertEqual([e.line for e in evlog.tail(LOG)], [1, 3, 5, 6, 8, 9, 11])
        self.assertEqual(evlog.tail(LOG, 0), [])
        self.assertEqual([e.line for e in evlog.tail(Source(LOG), 1)], [11])
        src = Source(LOG)
        with self.assertRaises(ValueError):
            evlog.tail(src, -1)
        self.assertEqual(src.reads, 0)

    def test_merge_defaults(self):
        got = evlog.merge([LOG, LOG_B])
        self.assertEqual([(i, e.line) for i, e in got],
                         [(1, 2), (0, 8), (0, 1), (0, 3), (0, 5), (1, 1), (0, 6), (1, 4), (0, 11), (0, 9)])
        self.assertEqual(evlog.merge([]), [])
        got = evlog.merge([Source(LOG_B), iter(LOG)])
        self.assertEqual([(i, e.line) for i, e in got][:4], [(0, 2), (1, 8), (1, 1), (0, 1)])

    def test_cli(self):
        fd, path = tempfile.mkstemp(suffix=".log")
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write("".join(LOG))
        try:
            out = io.StringIO()
            self.assertEqual(evlog.cli.main([path, "--top", "2"], out=out), 0)
            self.assertEqual(out.getvalue(), "total 7\nDEBUG 1\nINFO 3\nWARN 2\nERROR 1\n"
                             "first 2026-03-01T09:00:00\nlast 2026-03-01T11:00:00\n"
                             "top 2 request ok\ntop 2 slow request\n")
            out = io.StringIO()
            self.assertEqual(evlog.cli.main([path, "--min-level", "WARN", "--utc-offset", "60"], out=out), 0)
            self.assertEqual(out.getvalue(), "total 3\nDEBUG 0\nINFO 0\nWARN 2\nERROR 1\n"
                             "first 2026-03-01T08:00:00\nlast 2026-03-01T10:00:00\n")
            out = io.StringIO()
            self.assertEqual(evlog.cli.main([path, "--strict"], out=out), 2)
            self.assertEqual(out.getvalue(), "error: line 4: not TIMESTAMP LEVEL MESSAGE\n")
        finally:
            os.remove(path)


class NewInterface(unittest.TestCase):
    def test_parse_options_shape(self):
        PO = evlog.ParseOptions
        self.assertIs(evlog.reader.ParseOptions, PO)
        self.assertEqual([f.name for f in dataclasses.fields(PO)], ["min_level", "strict", "utc_offset"])
        o = PO()
        self.assertEqual((o.min_level, o.strict, o.utc_offset), ("DEBUG", False, 0))
        with self.assertRaises(dataclasses.FrozenInstanceError):
            o.strict = True
        with self.assertRaises(ValueError):
            PO(min_level="TRACE")

    def test_old_flags_rejected_at_call_time(self):
        calls = [
            lambda src: evlog.parse_events(src, "INFO"),
            lambda src: evlog.parse_events(src, True),
            lambda src: evlog.parse_events(src, {"strict": True}),
            lambda src: evlog.in_window(src, t(10), t(11), "INFO"),
            lambda src: evlog.summarize(src, "WARN"),
            lambda src: evlog.top_messages(src, 2, "INFO"),
            lambda src: evlog.tail(src, 2, "INFO"),
            lambda src: evlog.merge([src], "INFO"),
        ]
        for i, call in enumerate(calls):
            src = Source(LOG)
            with self.assertRaises(TypeError, msg=f"call {i}"):
                call(src)
            self.assertEqual(src.reads, 0, f"call {i} read input before rejecting options")

    def test_keyword_options(self):
        PO = evlog.ParseOptions
        self.assertEqual([e.line for e in evlog.parse_events(LOG, options=PO(min_level="WARN"))], [5, 8, 9])
        self.assertEqual(evlog.summarize(LOG, options=None), DEFAULT_SUMMARY)
        self.assertEqual([e.line for e in evlog.in_window(LOG, t(10), t(11), options=PO(min_level="INFO"))],
                         [3, 5, 6, 11])
        self.assertEqual(evlog.top_messages(LOG, n=1, options=PO(min_level="WARN")), [("slow request", 2)])

    def test_signatures(self):
        def shape(fn):
            return [(p.name, p.default) for p in inspect.signature(fn).parameters.values()]
        e = inspect.Parameter.empty
        self.assertEqual(shape(evlog.parse_events), [("lines", e), ("options", None)])
        self.assertEqual(shape(evlog.summarize), [("lines", e), ("options", None)])
        self.assertEqual(shape(evlog.top_messages), [("lines", e), ("n", 3), ("options", None)])
        self.assertEqual(shape(evlog.in_window), [("lines", e), ("start", e), ("end", e), ("options", None)])
        self.assertEqual(shape(evlog.tail), [("lines", e), ("n", 10), ("options", None)])
        self.assertEqual(shape(evlog.merge), [("sources", e), ("options", None)])


class Streaming(unittest.TestCase):
    def test_parse_events_is_lazy(self):
        src = Source(LOG)
        it = evlog.parse_events(src)
        self.assertIs(iter(it), it)
        self.assertEqual(src.reads, 0)
        self.assertEqual(next(it).line, 1)
        self.assertEqual(src.reads, 1)
        self.assertEqual(next(it).line, 3)
        self.assertEqual(src.reads, 3)

    def test_in_window_is_lazy(self):
        src = Source(LOG, limit=6)
        it = evlog.in_window(src, t(10), t(11))
        self.assertIs(iter(it), it)
        self.assertEqual([next(it).line for _ in range(3)], [3, 5, 6])

    def test_summarize_memory_is_flat(self):
        def lines(n):
            for i in range(n):
                yield f"2026-03-01T{i // 3600 % 24:02d}:{i // 60 % 60:02d}:{i % 60:02d} INFO message number {i}\n"
        tracemalloc.start()
        try:
            s = evlog.summarize(lines(50000))
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertEqual(s["total"], 50000)
        self.assertLess(peak, 2_000_000, f"peak {peak} bytes for 50000 events: events are being kept")

    def test_tail_memory_is_bounded(self):
        def lines(n):
            for i in range(n):
                yield f"2026-03-01T{i // 3600 % 24:02d}:{i // 60 % 60:02d}:{i % 60:02d} INFO message number {i}\n"
        tracemalloc.start()
        try:
            got = evlog.tail(lines(50000), 5)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertEqual([e.message for e in got], [f"message number {i}" for i in range(49995, 50000)])
        self.assertLess(peak, 2_000_000, f"peak {peak} bytes for the last 5 of 50000 events")

    def test_strict_error_arrives_in_order(self):
        PO = evlog.ParseOptions
        lines = ["2026-03-01T10:00:00 INFO a", "", "2026-03-01T10:01:00 INFO b",
                 "2026-03-01T10:02:00 TRACE c", "2026-03-01T10:03:00 INFO d"]
        it = evlog.parse_events(lines, PO(strict=True, min_level="ERROR"))
        with self.assertRaises(evlog.ParseError) as cm:
            next(it)
        self.assertTrue(str(cm.exception).startswith("line 4: unknown level TRACE"), str(cm.exception))
        it = evlog.parse_events(Source(lines), PO(strict=True))
        self.assertEqual([next(it).message, next(it).message], ["a", "b"])
        with self.assertRaises(evlog.ParseError) as cm:
            next(it)
        self.assertTrue(str(cm.exception).startswith("line 4: "), str(cm.exception))


class Options(unittest.TestCase):
    def test_negative_utc_offset_in_window(self):
        opts = evlog.ParseOptions(utc_offset=-90)
        got = list(evlog.in_window(LOG, t(11, 30), t(12, 30), opts))
        self.assertEqual([e.line for e in got], [3, 5, 6, 11])
        self.assertEqual(got[0].time, t(11, 30))

    def test_strict_through_callers(self):
        opts = evlog.ParseOptions(strict=True)
        for call in (lambda: evlog.summarize(LOG, opts), lambda: evlog.top_messages(LOG, 2, opts),
                     lambda: list(evlog.in_window(LOG, t(0), t(23), opts))):
            with self.assertRaises(evlog.ParseError) as cm:
                call()
            self.assertTrue(str(cm.exception).startswith("line 4: "), str(cm.exception))
        s = evlog.summarize(Source(LOG), evlog.ParseOptions(min_level="WARN", utc_offset=60))
        self.assertEqual((s["total"], s["first"], s["last"]), (3, "2026-03-01T08:00:00", "2026-03-01T10:00:00"))

    def test_top_messages_one_shot_with_options(self):
        got = evlog.top_messages(Source(LOG), 3, evlog.ParseOptions(min_level="INFO"))
        self.assertEqual(got, [("request ok", 2), ("slow request", 2), ("late arrival", 1)])

    def test_merge_and_tail_with_options(self):
        PO = evlog.ParseOptions
        got = evlog.merge([LOG, Source(LOG_B)], PO(min_level="WARN", utc_offset=60))
        self.assertEqual([(i, e.line) for i, e in got], [(0, 8), (0, 5), (1, 4), (0, 9)])
        self.assertEqual(got[2][1].time, t(9, 30))
        self.assertEqual([e.line for e in evlog.tail(Source(LOG), 2, PO(min_level="WARN"))], [8, 9])
        with self.assertRaises(evlog.ParseError) as cm:
            evlog.merge([LOG_B, LOG], PO(strict=True))
        self.assertTrue(str(cm.exception).startswith("line 3: "), str(cm.exception))


if __name__ == "__main__":
    unittest.main()
