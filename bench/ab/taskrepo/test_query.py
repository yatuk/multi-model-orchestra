import unittest

from query import ParseError, matches, parse


class TestQuery(unittest.TestCase):
    def test_single(self):
        self.assertEqual(parse("age >= 18"), ("cmp", "age", ">=", 18))

    def test_and_or_precedence(self):
        self.assertEqual(
            parse('a = 1 OR b = "x" AND c != 2'),
            ("or", ("cmp", "a", "=", 1), ("and", ("cmp", "b", "=", "x"), ("cmp", "c", "!=", 2))),
        )

    def test_error_position(self):
        with self.assertRaises(ParseError) as cm:
            parse("a = 1 AND")
        self.assertEqual(cm.exception.pos, 9)

    def test_matches(self):
        self.assertTrue(matches("user.age > 20 AND NOT banned = true", {"user": {"age": 30}, "banned": False}))


if __name__ == "__main__":
    unittest.main()
