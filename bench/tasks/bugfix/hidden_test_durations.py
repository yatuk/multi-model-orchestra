"""Held-out tests: the lane never sees this file. They check every rule in the docstring."""
import unittest

from durations import parse_duration


class HiddenTests(unittest.TestCase):
    def test_happy(self):
        self.assertEqual(parse_duration("0s"), 0)
        self.assertEqual(parse_duration("10m"), 600)
        self.assertEqual(parse_duration("1h0m0s"), 3600)

    def test_duplicate_unit(self):
        for bad in ("1h1h", "5s5s", "1m2m"):
            with self.assertRaises(ValueError, msg=bad):
                parse_duration(bad)

    def test_order(self):
        for bad in ("1m1h", "5s1m", "1s1h"):
            with self.assertRaises(ValueError, msg=bad):
                parse_duration(bad)

    def test_unit_without_number(self):
        for bad in ("h", "1hm", "m5s"):
            with self.assertRaises(ValueError, msg=bad):
                parse_duration(bad)

    def test_trailing_number(self):
        with self.assertRaises(ValueError):
            parse_duration("1h30")

    def test_other_chars(self):
        for bad in (" 1h", "1h ", "-1h", "1d", "1H"):
            with self.assertRaises(ValueError, msg=bad):
                parse_duration(bad)


if __name__ == "__main__":
    unittest.main()
