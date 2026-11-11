import unittest

from durations import parse_duration


class VisibleTests(unittest.TestCase):
    def test_full(self):
        self.assertEqual(parse_duration("1h30m15s"), 5415)

    def test_subset(self):
        self.assertEqual(parse_duration("45s"), 45)
        self.assertEqual(parse_duration("2h5s"), 7205)

    def test_trailing_number(self):
        with self.assertRaises(ValueError):
            parse_duration("90")

    def test_empty(self):
        with self.assertRaises(ValueError):
            parse_duration("")


if __name__ == "__main__":
    unittest.main()
