import time
import unittest

from cache import LRUCache


class FakeClock:
    def __init__(self):
        self.now = 100.0

    def __call__(self):
        return self.now


class HiddenCache(unittest.TestCase):
    def test_put_refreshes_ttl(self):
        clock = FakeClock()
        c = LRUCache(4, ttl=10, clock=clock)
        c.put("a", 1)
        clock.now = 108
        c.put("a", 2)
        clock.now = 115
        self.assertEqual(c.get("a"), 2)

    def test_get_does_not_refresh_ttl(self):
        clock = FakeClock()
        c = LRUCache(4, ttl=10, clock=clock)
        c.put("a", 1)
        clock.now = 105
        c.get("a")
        clock.now = 110
        self.assertIsNone(c.get("a"))

    def test_expired_not_counted(self):
        clock = FakeClock()
        c = LRUCache(4, ttl=5, clock=clock)
        c.put("a", 1)
        c.put("b", 2)
        clock.now = 103
        c.put("c", 3)
        clock.now = 106
        self.assertEqual(len(c), 1)
        self.assertNotIn("a", c)
        self.assertIn("c", c)

    def test_expired_frees_capacity(self):
        clock = FakeClock()
        c = LRUCache(2, ttl=5, clock=clock)
        c.put("a", 1)
        clock.now = 103
        c.put("b", 2)
        clock.now = 106
        c.put("c", 3)
        self.assertEqual(c.get("b"), 2)
        self.assertEqual(c.get("c"), 3)

    def test_default_value(self):
        clock = FakeClock()
        c = LRUCache(2, ttl=1, clock=clock)
        c.put("a", 1)
        clock.now = 200
        self.assertEqual(c.get("a", "gone"), "gone")

    def test_bad_ttl(self):
        for bad in (0, -1):
            with self.assertRaises(ValueError):
                LRUCache(2, ttl=bad)

    def test_default_clock_is_monotonic(self):
        c = LRUCache(2, ttl=60)
        c.put("a", 1)
        self.assertEqual(c.get("a"), 1)
        self.assertIs(c.clock, time.monotonic)

    def test_lru_still_works_with_ttl(self):
        clock = FakeClock()
        c = LRUCache(2, ttl=100, clock=clock)
        c.put("a", 1)
        c.put("b", 2)
        c.get("a")
        c.put("c", 3)
        self.assertNotIn("b", c)


if __name__ == "__main__":
    unittest.main()
