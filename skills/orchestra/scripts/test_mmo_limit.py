"""Tests for the return-time parser (mmo_limit.py) and the usage reader (mmo_usage.py). Offline.

  python -m pytest skills/orchestra/scripts/test_mmo_limit.py -q

Every time here is checked against a fixed "now" and a fixed zone, so the result does not depend on the
clock or the machine's own time zone.
"""
import datetime
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mmo_limit  # noqa: E402
import mmo_usage  # noqa: E402

UTC = datetime.timezone.utc
NOW = datetime.datetime(2026, 11, 28, 10, 0, 0, tzinfo=UTC)


def parse(text, now=NOW):
    return mmo_limit.parse_retry_time(text, now)


class RetryTime(unittest.TestCase):
    def test_codex_message_with_full_date_and_year(self):
        msg = "You've hit your usage limit. Upgrade to Pro or try again at Dec 21st, 2026 9:18 AM."
        got = datetime.datetime.strptime(parse(msg), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        # No zone is named, so the text is the machine's local time: compare in that zone.
        local = got.astimezone()
        self.assertEqual((local.year, local.month, local.day, local.hour, local.minute), (2026, 12, 21, 9, 18))

    def test_full_date_in_a_named_zone(self):
        self.assertEqual(parse("try again at Dec 21st, 2026 9:18 AM (UTC)"), "2026-12-21T09:18:00Z")
        self.assertEqual(parse("try again at Dec 21, 2026 9:18 PM (Europe/Istanbul)"), "2026-12-21T18:18:00Z")

    def test_date_without_year_is_the_next_occurrence(self):
        self.assertEqual(parse("try again at Dec 3 9:00 AM (UTC)"), "2026-12-03T09:00:00Z")
        # Nov 28 8:00 UTC is already past at 10:00, so the next one is a year away: too far to trust.
        self.assertIsNone(parse("try again at Nov 28 8:00 AM (UTC)"))

    def test_bare_hour_needs_a_zone(self):
        self.assertEqual(parse("resets 4pm (Europe/Istanbul)"), "2026-11-28T13:00:00Z")
        self.assertIsNone(parse("resets 4pm"))
        self.assertIsNone(parse("resets 4pm (Not/AZone)"))

    def test_bare_hour_already_past_today_means_tomorrow(self):
        # 09:00 Istanbul is 06:00 UTC, before NOW, so the next one is tomorrow.
        self.assertEqual(parse("resets 9am (Europe/Istanbul)"), "2026-11-29T06:00:00Z")
        self.assertEqual(parse("resets 4:30pm (UTC)"), "2026-11-28T16:30:00Z")

    def test_retry_after_seconds(self):
        self.assertEqual(parse("HTTP 429 openrouter: Rate limit reached (Retry-After: 120)"), "2026-11-28T10:02:00Z")
        self.assertEqual(parse("retry-after: 45s"), "2026-11-28T10:00:45Z")

    def test_retry_after_http_date(self):
        self.assertEqual(parse("Retry-After: Sun, 29 Nov 2026 07:28:00 GMT"), "2026-11-29T07:28:00Z")

    def test_retry_after_in_other_units_is_not_read_as_seconds(self):
        self.assertIsNone(parse("Retry-After: 5 minutes"))

    def test_garbage_and_unsure_input_is_not_guessed(self):
        for text in ["", None, "garbage", "try again later", "Retry-After: 0", "try again at Dec 3",
                     "Feb 30 9:00 AM (UTC)", "at 25:99", "limit reached 1234567", "resets soon (Europe/Istanbul)"]:
            self.assertIsNone(parse(text), text)

    def test_past_and_far_times_are_refused(self):
        self.assertIsNone(parse("try again at Jan 1, 2020 9:00 AM (UTC)"))
        self.assertIsNone(parse("try again at Dec 21st, 2027 9:18 AM (UTC)"))
        self.assertIsNone(parse("Retry-After: 99999999"))

    def test_stored_time_helpers(self):
        self.assertIsNotNone(mmo_limit.future("2999-01-01T00:00:00Z"))
        self.assertIsNone(mmo_limit.future("2020-01-01T00:00:00Z"))
        self.assertIsNone(mmo_limit.future("next tuesday"))
        self.assertIsNone(mmo_limit.future(None))
        self.assertEqual(mmo_limit.local_text("junk"), "")
        self.assertRegex(mmo_limit.local_text("2026-12-21T06:18:00Z"), r"^2026-12-2[01] \d\d:\d\d$")


CLAUDE = {"type": "result", "result": "PONG", "total_cost_usd": 0.0123,
          "usage": {"input_tokens": 1200, "output_tokens": 80, "cache_read_input_tokens": 900,
                    "cache_creation_input_tokens": 50},
          "modelUsage": {"claude-sonnet-4-6": {"outputTokens": 80}}}


class Usage(unittest.TestCase):
    def test_claude_shape(self):
        u = mmo_usage.usage_of("claude", json.dumps(CLAUDE), "sonnet")
        self.assertEqual((u["tokens_in"], u["tokens_out"], u["tokens_cached"], u["cost_usd"]), (1200, 80, 900, 0.0123))
        self.assertEqual(u["served_model"], "claude-sonnet-4-6")
        self.assertEqual(mmo_usage.header_fields(u, "sonnet"), " in=1200 out=80 cached=900 cost=0.0123")

    def test_other_served_model_is_in_the_header(self):
        u = mmo_usage.usage_of("claude", json.dumps(CLAUDE), "opus")
        self.assertTrue(mmo_usage.header_fields(u, "opus").endswith(" served=claude-sonnet-4-6"))

    def test_event_list_and_vendor_lanes(self):
        u = mmo_usage.usage_of("claude-kimi", json.dumps([{"type": "system"}, CLAUDE]), "kimi-k3")
        self.assertEqual(u["tokens_out"], 80)

    def test_absent_fields_stay_absent(self):
        u = mmo_usage.usage_of("claude", json.dumps({"result": "x", "usage": {"output_tokens": 5}}), "sonnet")
        self.assertEqual(u, {"tokens_out": 5})
        self.assertEqual(mmo_usage.header_fields(u, "sonnet"), " out=5")
        self.assertEqual(mmo_usage.usage_of("claude", "not json", "sonnet"), {})

    def test_junk_numbers_are_dropped(self):
        bad = {"result": "x", "total_cost_usd": "free", "usage": {"input_tokens": -3, "output_tokens": True}}
        self.assertEqual(mmo_usage.usage_of("claude", json.dumps(bad), "sonnet"), {})

    def test_budget_stop_is_the_cost_ceiling(self):
        u = mmo_usage.usage_of("claude", json.dumps({"subtype": "error_max_budget_usd", "total_cost_usd": 0.5}), "sonnet")
        self.assertEqual(u["ceiling"], "cost")
        self.assertNotIn("ceiling", mmo_usage.usage_of("claude", json.dumps(CLAUDE), "sonnet"))

    def test_lanes_without_a_known_shape_report_nothing(self):
        for lane in ("grok", "opencode", "agy", "gemini", "qwen", "codex", "vibe"):
            self.assertEqual(mmo_usage.usage_of(lane, json.dumps(CLAUDE), "m"), {}, lane)

    def test_api_side_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "side.json")
            with open(path, "w") as f:
                json.dump({"usage": {"prompt_tokens": 100, "completion_tokens": 20, "total_tokens": 120, "cost": 0.0042},
                           "model": "vendor/x"}, f)
            u = mmo_usage.usage_of("api", "", "ep:model", path)
            self.assertEqual((u["tokens_in"], u["tokens_out"], u["cost_usd"], u["served_model"]), (100, 20, 0.0042, "vendor/x"))
            self.assertEqual(mmo_usage.header_fields(u, "ep:model"), " in=100 out=20 cost=0.0042 served=vendor/x")
            self.assertEqual(mmo_usage.usage_of("api", "", "ep:model", os.path.join(d, "missing.json")), {})
            self.assertEqual(mmo_usage.log_fragment({}), "")


if __name__ == "__main__":
    unittest.main()
