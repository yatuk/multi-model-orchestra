import unittest

from intervals import merge


class HiddenMerge(unittest.TestCase):
    def test_touching(self):
        self.assertEqual(merge([(3, 6), (1, 3)]), [(1, 6)])

    def test_one_apart(self):
        self.assertEqual(merge([(1, 3), (4, 6)]), [(1, 3), (4, 6)])

    def test_contained(self):
        self.assertEqual(merge([(1, 10), (2, 3), (4, 5)]), [(1, 10)])

    def test_point(self):
        self.assertEqual(merge([(4, 4), (4, 4), (7, 7)]), [(4, 4), (7, 7)])

    def test_bad_interval(self):
        with self.assertRaises(ValueError) as cm:
            merge([(1, 2), (5, 3)])
        self.assertIn("5", str(cm.exception))

    def test_input_untouched(self):
        data = [(5, 6), (1, 2)]
        merge(data)
        self.assertEqual(data, [(5, 6), (1, 2)])

    def test_chain(self):
        self.assertEqual(merge([(1, 2), (2, 3), (3, 4), (9, 9), (0, 1)]), [(0, 4), (9, 9)])

    def test_lists_in_tuples_out(self):
        self.assertEqual(merge([[1, 3], [2, 4]]), [(1, 4)])


if __name__ == "__main__":
    unittest.main()
