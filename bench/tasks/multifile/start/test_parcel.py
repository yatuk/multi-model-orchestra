import unittest

from parcel import Item, Order, quote, quote_text


class VisibleTests(unittest.TestCase):
    def test_simple_quote(self):
        self.assertEqual(quote(Order("DOM", [Item("mug", "300g")])), 450)

    def test_fuel_surcharge(self):
        self.assertEqual(quote(Order("EU", [Item("book", "0.4kg")]), fuel_percent=10), 1089)

    def test_quote_text(self):
        order = Order("EU", [Item("lamp", "1.2kg")])
        self.assertEqual(quote_text(order), "EU 16.90 EUR (1.240 kg)")

    def test_repeat_quote_is_stable(self):
        order = Order("DOM", [Item("mug", "300g"), Item("tea", "50g", qty=2)])
        first = quote(order, fuel_percent=10)
        second = quote(order, fuel_percent=10)
        self.assertEqual(first, 495)
        self.assertEqual(second, first)


if __name__ == "__main__":
    unittest.main()
