import unittest

from intervals import merge


class TestMerge(unittest.TestCase):
    def test_overlap(self):
        self.assertEqual(merge([(1, 5), (3, 8)]), [(1, 8)])

    def test_unsorted(self):
        self.assertEqual(merge([(10, 12), (1, 2)]), [(1, 2), (10, 12)])

    def test_empty(self):
        self.assertEqual(merge([]), [])


if __name__ == "__main__":
    unittest.main()
