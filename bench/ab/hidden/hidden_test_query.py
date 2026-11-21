import unittest

from query import ParseError, matches, parse


class HiddenParse(unittest.TestCase):
    def test_values(self):
        self.assertEqual(parse("x = -5"), ("cmp", "x", "=", -5))
        self.assertEqual(parse("x = true"), ("cmp", "x", "=", True))
        self.assertEqual(parse("x != null"), ("cmp", "x", "!=", None))
        self.assertEqual(parse('x = "a \\"b\\" \\\\ c"'), ("cmp", "x", "=", 'a "b" \\ c'))

    def test_left_assoc(self):
        self.assertEqual(
            parse("a=1 and b=2 and c=3"),
            ("and", ("and", ("cmp", "a", "=", 1), ("cmp", "b", "=", 2)), ("cmp", "c", "=", 3)),
        )

    def test_parens_and_not(self):
        self.assertEqual(
            parse("NOT (a < 1 or b > 2) AND not c <= 3"),
            ("and", ("not", ("or", ("cmp", "a", "<", 1), ("cmp", "b", ">", 2))), ("not", ("cmp", "c", "<=", 3))),
        )

    def test_double_not(self):
        self.assertEqual(parse("NOT NOT a = 1"), ("not", ("not", ("cmp", "a", "=", 1))))

    def test_whitespace(self):
        self.assertEqual(parse("  (a>=1)OR(b=2)  "), ("or", ("cmp", "a", ">=", 1), ("cmp", "b", "=", 2)))

    def test_dotted_field(self):
        self.assertEqual(parse("user.address_2.zip = 1"), ("cmp", "user.address_2.zip", "=", 1))

    def test_errors(self):
        cases = {"": 0, "a = ": 4, "a == 1": 3, "(a = 1": 6, "a = 1)": 5, 'a = "open': 4, "= 1": 0, "a = 1 b = 2": 6}
        for text, pos in cases.items():
            with self.subTest(text=text):
                with self.assertRaises(ParseError) as cm:
                    parse(text)
                self.assertEqual(cm.exception.pos, pos)

    def test_parse_error_is_value_error(self):
        self.assertTrue(issubclass(ParseError, ValueError))


class HiddenMatches(unittest.TestCase):
    REC = {"name": "ann", "age": 41, "tags": None, "meta": {"score": 2.5}}

    def test_basic(self):
        self.assertTrue(matches('name = "ann" and age > 40', self.REC))
        self.assertFalse(matches('name = "bob" or age < 40', self.REC))

    def test_missing_field_is_false(self):
        self.assertFalse(matches("nope != 1", self.REC))
        self.assertTrue(matches("NOT nope = 1", self.REC))
        self.assertFalse(matches("meta.missing.deeper = 1", self.REC))

    def test_null(self):
        self.assertTrue(matches("tags = null", self.REC))

    def test_type_mismatch_is_false(self):
        self.assertFalse(matches('age > "a"', self.REC))
        self.assertFalse(matches('name < 3', self.REC))

    def test_int_float_compare(self):
        self.assertTrue(matches("meta.score > 2", self.REC))

    def test_bool_not_int(self):
        self.assertFalse(matches("flag = 1", {"flag": True}))


if __name__ == "__main__":
    unittest.main()
