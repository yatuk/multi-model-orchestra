import unittest

from cache import LRUCache


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


class TestLRU(unittest.TestCase):
    def test_evicts_least_recent(self):
        c = LRUCache(2)
        c.put("a", 1)
        c.put("b", 2)
        c.get("a")
        c.put("c", 3)
        self.assertNotIn("b", c)
        self.assertEqual(c.get("a"), 1)

    def test_ttl_expires(self):
        clock = FakeClock()
        c = LRUCache(4, ttl=10, clock=clock)
        c.put("a", 1)
        clock.now = 9.5
        self.assertEqual(c.get("a"), 1)
        clock.now = 10.0
        self.assertIsNone(c.get("a"))

    def test_no_ttl_by_default(self):
        clock = FakeClock()
        c = LRUCache(2, clock=clock)
        c.put("a", 1)
        clock.now = 1e9
        self.assertEqual(c.get("a"), 1)


if __name__ == "__main__":
    unittest.main()
