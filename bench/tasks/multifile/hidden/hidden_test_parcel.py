"""Held-out tests for the multifile task. The lane never sees this file.

Four groups, one class each, so partial credit says what was fixed:
  KeepWorking   behaviour that already works on the starting code and must keep working
  RepeatQuotes  the reported symptom and its cause (a quote must not change shared state)
  Rounding      a quieter defect: half-cent surcharges round half up, as documented
  Zones         another quiet one: zone codes are case-insensitive in every path
Names are reached through the module (parcel.quote), not imported at the top, so one
missing name fails the tests that need it instead of the whole file.
"""
import unittest

import parcel

# Public names these tests use. The grader checks each one still exists.
PUBLIC = [
    "parcel.parse_weight", "parcel.Item", "parcel.Order", "parcel.QuoteError", "parcel.quote",
    "parcel.quote_text", "parcel.table_for", "parcel.apply_fuel", "parcel.fuel_amount",
]


def fresh():
    """Forget cached tables, so one group's leftovers cannot fail another group."""
    import parcel.rates
    cache = getattr(parcel.rates, "_CACHE", None)
    if isinstance(cache, dict):
        cache.clear()


def order(zone, *items):
    return parcel.Order(zone, [parcel.Item(*i) for i in items])


class KeepWorking(unittest.TestCase):
    def setUp(self):
        fresh()

    def test_parse_weight(self):
        cases = {"250g": 250, "1.2kg": 1200, "1lb": 454, "0.5oz": 15, "0.1g": 1, "0g": 0,
                 "2.5lb": 1134, "16oz": 454, "0.001kg": 1}
        for text, grams in cases.items():
            self.assertEqual(parcel.parse_weight(text), grams, text)

    def test_bad_input_raises(self):
        for bad in (" 1g", "1 g", "-1g", "1G", "1e3g", "1,000g", "g", "1.g", ".5kg", "1t", ""):
            with self.assertRaises(parcel.QuoteError, msg=repr(bad)):
                parcel.parse_weight(bad)
        with self.assertRaises(parcel.QuoteError):
            parcel.Item("x", "1g", qty=0)
        with self.assertRaises(parcel.QuoteError):
            parcel.quote(order("MARS", ("x", "1kg")))
        with self.assertRaises(parcel.QuoteError):
            parcel.quote(parcel.Order("DOM"))
        for pct in (51, -1, 2.5):
            fresh()
            with self.assertRaises(parcel.QuoteError, msg=repr(pct)):
                parcel.quote(order("DOM", ("x", "1kg")), fuel_percent=pct)

    def test_brackets_and_overweight(self):
        cases = [
            ("DOM", "460g", 450), ("DOM", "461g", 625), ("EU", "9960g", 2450), ("EU", "9961g", 2710),
            ("DOM", "6960g", 1585), ("WORLD", "12kg", 7210), ("WORLD", "460g", 1890),
        ]
        for zone, weight, cents in cases:
            fresh()
            self.assertEqual(parcel.quote(order(zone, ("x", weight))), cents, f"{zone} {weight}")

    def test_order_weight_and_text(self):
        o = order("WORLD", ("a", "1lb", 3))
        self.assertEqual(o.total_grams(), 1402)
        self.assertEqual(parcel.Order("EU").total_grams(), 0)
        self.assertEqual(order("EU", ("a", 100), ("b", 60, 2)).total_grams(), 260)
        self.assertEqual(parcel.quote_text(o), "WORLD 31.25 EUR (1.402 kg)")

    def test_zone_any_case_within_brackets(self):
        self.assertEqual(parcel.quote(order("eu", ("x", "400g"))), 990)
        fresh()
        self.assertEqual(parcel.quote(order("World", ("x", "1.9kg")), fuel_percent=20), 3750)
        with self.assertRaises(parcel.QuoteError):
            parcel.quote(order("mars", ("x", "1kg")))


class RepeatQuotes(unittest.TestCase):
    """No fresh() between quotes here: carrying state from one quote to the next is the bug."""

    def setUp(self):
        fresh()

    def test_same_order_three_times(self):
        o = order("DOM", ("mug", "300g"), ("tea", "100g"))
        self.assertEqual([parcel.quote(o, fuel_percent=10) for _ in range(3)], [495, 495, 495])

    def test_fuel_then_no_fuel(self):
        o = order("EU", ("book", "0.4kg"))
        self.assertEqual(parcel.quote(o, fuel_percent=10), 1089)
        self.assertEqual(parcel.quote(o), 990)
        self.assertEqual(parcel.quote(o, fuel_percent=20), 1188)
        self.assertEqual(parcel.quote(o), 990)

    def test_cached_table_unchanged(self):
        for pct in (10, 20, 30):
            parcel.quote(order("DOM", ("x", "1.5kg")), fuel_percent=pct)
        self.assertEqual(list(parcel.table_for("DOM")), [(500, 450), (1000, 625), (2000, 890), (5000, 1225)])

    def test_apply_fuel_returns_new_table(self):
        table = [(500, 100), (1000, 200)]
        result = parcel.apply_fuel(table, 10)
        self.assertEqual(table, [(500, 100), (1000, 200)])
        self.assertEqual(list(result), [(500, 110), (1000, 220)])
        self.assertIsNot(result, table)

    def test_overweight_repeat(self):
        o = order("DOM", ("anvil", "6960g"))
        self.assertEqual(parcel.quote(o, fuel_percent=20), 1830)
        self.assertEqual(parcel.quote(o, fuel_percent=20), 1830)


class Rounding(unittest.TestCase):
    """One quote per fresh cache, so these do not depend on the RepeatQuotes fix."""

    def q(self, zone, weight, pct):
        fresh()
        return parcel.quote(order(zone, ("x", weight)), fuel_percent=pct)

    def test_half_cent_rounds_up_dom(self):
        self.assertEqual(self.q("DOM", "960g", 10), 688)
        self.assertEqual(self.q("DOM", "4960g", 2), 1250)
        self.assertEqual(self.q("DOM", "1960g", 10), 979)

    def test_half_cent_rounds_up_eu_world(self):
        self.assertEqual(self.q("EU", "960g", 5), 1313)
        self.assertEqual(self.q("WORLD", "1960g", 2), 3188)
        self.assertEqual(self.q("WORLD", "460g", 50), 2835)

    def test_fuel_amount_and_text(self):
        cases = [((1225, 2), 25), ((25, 2), 1), ((122, 2), 2), ((1249, 2), 25), ((1224, 2), 24),
                 ((125, 2), 3), ((0, 50), 0), ((1, 50), 1)]
        for args, cents in cases:
            self.assertEqual(parcel.fuel_amount(*args), cents, args)
        fresh()
        self.assertEqual(parcel.quote_text(order("DOM", ("x", "960g")), fuel_percent=10), "DOM 6.88 EUR (1.000 kg)")


class Zones(unittest.TestCase):
    """Zone codes are case-insensitive everywhere, not only where a table is looked up."""

    def setUp(self):
        fresh()

    def test_any_case_above_last_bracket(self):
        self.assertEqual(parcel.quote(order("eu", ("x", "9961g"))), 2710)
        fresh()
        self.assertEqual(parcel.quote(order("World", ("x", "12kg"))), 7210)

    def test_any_case_in_text(self):
        self.assertEqual(parcel.quote_text(order("dom", ("x", "300g"))), "DOM 4.50 EUR (0.340 kg)")


if __name__ == "__main__":
    unittest.main()
